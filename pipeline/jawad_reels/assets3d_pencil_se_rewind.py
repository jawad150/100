"""assets3d_pencil_se_rewind.py - photoreal Blender props for Bijli series #1 "Pencil Se Rewind" (@jawad_mp4).

Builds the render list of brand_reels/design/reels/pencil_se_rewind/SHOTS.md section A with bpy 5.2 / Cycles
(adaptive sampling + OpenImageDenoise with albedo/normal guides, fixed seed, view transform Standard, look None,
gamma 1) as RGBA 8-bit straight-alpha sRGB PNGs in the shared 3D asset spec:

    Device: assets3d_gpu.set_device (called from reset()). CPU by default (here: tests / previews only, threads 2);
    FOSTER_GPU=1 picks OPTIX > CUDA > HIP > METAL > ONEAPI (finals: RTX 4060 OptiX, 8 GB) and switches every asset to
    its GPU sample count (gpu_spp, 256-1024, adaptive threshold 0.01, OIDN on the GPU). The device lands in the log
    line "[assets3d] Cycles device: ..." and in meta.json "device". Never mix CPU and GPU frames in one folder.
    All paths are os.path joins (Windows-safe); nothing here shells out. Final commands: RENDER_JOBS.md.

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
    python3 assets3d_pencil_se_rewind.py textures       # regenerate the procedural texture maps (needs the fonts)
    python3 assets3d_pencil_se_rewind.py savetex        # copy the maps to brand_reels/assets/pencil_se_rewind/tex3d
    python3 assets3d_pencil_se_rewind.py cams [names]   # build the scenes, print + save the feature px (no render)
    python3 assets3d_pencil_se_rewind.py restore        # rebuild the PNG folders from the committed pack
    python3 assets3d_pencil_se_rewind.py sheet          # contact sheet of the finals
    python3 assets3d_pencil_se_rewind.py previewsheet   # the same for the --preview renders
    python3 assets3d_pencil_se_rewind.py pack           # compressed copies into brand_reels/assets/pencil_se_rewind/assets3d

    --preview   16 spp, half resolution, written to RWS/out/preview3d/<name>/passes/ (finals untouched)
    --frames    render only these frame indices (tests; meta.json is not written)
    env FOSTER_GPU=1 (GPU finals), FOSTER_GPU_TYPE=CUDA (force a backend), PSR_THREADS (CPU threads, default 2),
    PSR_OUT (default RWS/assets3d), SKIP_EXISTING=1 (resume a folder on the same device). On the shared Linux box
    every render goes through tools/heavy.sh; on the GPU PC run the python lines of RENDER_JOBS.md directly.
    Textures missing from RWS/out/tex3d are restored from brand_reels/assets/pencil_se_rewind/tex3d first.

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
TEX_PACK = os.path.join(REPO, 'brand_reels', 'assets', REEL, 'tex3d')
THREADS = int(os.environ.get('PSR_THREADS', '2'))
FONT_HAND = os.path.join(H.FONTS, 'Caveat-Bold.ttf')
FONT_SANS = os.path.join(H.FONTS, 'Poppins-SemiBold.ttf')
MM = 0.001
S_PREVIEW = 16
CROP_PAD = 24
EXPOSURE = float(os.environ.get('PSR_EXPOSURE', '-0.8'))

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
    dust = np.maximum(dust, np.clip((_fbm(S, S, (600, 200, 60), 4) - 0.62) / 0.30, 0, 1) * 0.12)   # soft haze
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    xm = xx / ppm - DESK_TEX_M / 2
    ym = DESK_TEX_M / 2 - yy / ppm
    blob = _fbm(S, S, (500, 160, 50), 11)
    rr = np.hypot((xm - 0.150) / 1.4, ym + 0.105)
    ink = np.clip((0.034 - rr) / 0.012 + (blob - 0.5) * 1.6, 0, 1)
    ink = np.maximum(ink, np.clip((0.007 - np.hypot(xm - 0.188, ym + 0.082)) / 0.002 + (blob - 0.5), 0, 1))
    ink = cv2.GaussianBlur(ink, (0, 0), 3) * (0.75 + 0.25 * _fbm(S, S, (60, 20), 12))
    worn = 0.6 * _fbm(S, S, (700, 240), 13) + 0.4 * _fbm(S, S, (90, 30), 14)     # broken-up, low-contrast wear
    worn = np.clip((worn - 0.35) / 0.45, 0, 1) ** 1.5
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


TEX_FILES = ['label_a.png', 'label_a_ink.png', 'label_b.png', 'wear.png', 'desk.png', 'hb.png', 'battery.png'] + \
    [f'key_{k}.png' for k in W_KEYS]


def build_textures(force=False):
    """Texture maps into RWS/out/tex3d. A missing map is first restored from the committed copies in
    brand_reels/assets/pencil_se_rewind/tex3d (same pixels on every machine, no fonts needed), else generated.
    force=True regenerates everything (needs the Caveat / Poppins fonts in the workspace fonts folder)."""
    import shutil
    os.makedirs(TEX, exist_ok=True)
    if not force:
        for fn in TEX_FILES:
            src = os.path.join(TEX_PACK, fn)
            if not os.path.exists(_tex_path(fn)) and os.path.exists(src):
                shutil.copy2(src, _tex_path(fn))
    jobs = [('label_a.png', tex_label), ('wear.png', tex_wear), ('desk.png', tex_desk), ('hb.png', tex_hb),
            ('battery.png', tex_battery), ('key_rew.png', tex_keys)]
    for fn, job in jobs:
        if force or not os.path.exists(_tex_path(fn)):
            t0 = time.time()
            job()
            print(f'[tex] {fn} {time.time() - t0:.1f}s', flush=True)


def save_textures():
    """Copy the current texture maps into brand_reels/assets/pencil_se_rewind/tex3d (committed)."""
    import shutil
    build_textures()
    os.makedirs(TEX_PACK, exist_ok=True)
    for fn in TEX_FILES:
        shutil.copy2(_tex_path(fn), os.path.join(TEX_PACK, fn))
    print('saved', TEX_PACK)


# ============================================================================= bpy helpers

def _bpy():
    global bpy, Vector
    if bpy is None:
        B._bpy()
        import bpy as _b
        from mathutils import Vector as _V
        bpy, Vector = _b, _V
    return bpy


DEVICE = 'CPU'


def is_gpu():
    return not DEVICE.startswith('CPU')


def reset(res, samples):
    """Empty Cycles scene (H.reset: factory settings, OIDN albedo+normal, Standard view, RGBA 8-bit PNG) with this
    reel's settings. Device: assets3d_gpu.set_device -> CPU unless FOSTER_GPU=1 finds a GPU (OPTIX > CUDA > ...)."""
    global DEVICE
    import assets3d_gpu
    sc = H.reset(res, samples, 'night')
    DEVICE = assets3d_gpu.set_device(bpy, sc)          # idempotent; H.reset already called it, this returns the name
    if is_gpu():
        sc.render.threads_mode = 'AUTO'                 # CPU only syncs the scene; let it use every core
        if hasattr(sc.cycles, 'denoising_use_gpu'):
            sc.cycles.denoising_use_gpu = True
    else:
        sc.render.threads_mode = 'FIXED'
        sc.render.threads = THREADS
    sc.cycles.samples = samples
    sc.cycles.adaptive_threshold = 0.01 if is_gpu() else 0.02
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
    sc.view_settings.exposure = EXPOSURE      # brightest lamp-pool diffuse (label paper) <= 0.85, SHOTS.md
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


def shadow_tint(m, tint):
    """Clear / smoked plastic and glass: shadow rays pass through tinted (Transparent BSDF) instead of being blocked
    by the refractive BSDF, so the parts behind a window (cassette inside the walkman, hubs and tape packs inside the
    shell) get the lamp's direct light without caustics. Camera / reflection rays still see the full glass shader."""
    nt = m.node_tree
    out = nt.nodes['Material Output']
    src = out.inputs['Surface'].links[0].from_socket
    lp = nt.nodes.new('ShaderNodeLightPath')
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    tr.inputs[0].default_value = tuple(tint) + (1.0,)
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Shadow Ray'], mx.inputs[0])
    nt.links.new(src, mx.inputs[1])
    nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs['Surface'])
    return m


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
    return shadow_tint(m, (0.62, 0.42, 0.26))


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
    return shadow_tint(m, (0.90, 0.82, 0.72))


def m_grip():
    m, b, g = B.principled('grip_ps', mixl('SHELL', '#B07A4E', 0.45), rough=0.30, ior=1.59)
    b.inputs['Transmission Weight'].default_value = 0.6
    x, y, z = g.xyz(g.co('Object'))
    rib = g.m('SINE', g.m('MULTIPLY', y, 2 * math.pi / 0.0009))
    g.put(b.inputs['Normal'], g.bump(rib, 0.5, 0.00008))
    return shadow_tint(m, (0.45, 0.30, 0.19))


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
    cr = g.m('MULTIPLY_ADD', worn, 0.20, 0.24)
    cr = g.m('MAXIMUM', cr, g.m('MULTIPLY', scr, 0.7))
    cr = g.m('MAXIMUM', cr, g.m('MULTIPLY', dust, 0.9))
    g.put(b.inputs['Coat Roughness'], cr)
    g.put(b.inputs['Coat Weight'], g.m('MULTIPLY_ADD', worn, -0.20, 1.0))
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
    # (lid object coords are hinge coords: x 0 .. L_LEN from the hinge, y as the body; corner = free edge, back)
    edge_n = g.m('MULTIPLY', g.noise(co, 700.0, 4.0, 0.6), 0.0016)
    sx = g.mr(g.m('ADD', x, edge_n), L_LEN - 0.0235, L_LEN - 0.0215, 0.0, 1.0)
    sy = g.mr(g.m('ADD', y, edge_n), W_LID['y1'] - 0.0170, W_LID['y1'] - 0.0150, 0.0, 1.0)
    rag = g.mr(g.noise(co, 260.0, 3.0, 0.5), 0.30, 0.70, 0.55, 1.0)
    st = g.m('MULTIPLY', g.m('MULTIPLY', sx, sy), g.m('MULTIPLY', rag, 0.85), clamp=True)
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
    m, b, g = B.principled('lid_window', (0.58, 0.45, 0.33), rough=0.03, ior=1.52)
    b.inputs['Transmission Weight'].default_value = 0.92
    scr, fin, dust = wear_maps(g, 13.0, offset=(0.8, 0.5))
    r = g.m('MULTIPLY_ADD', scr, 0.10, 0.03)
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', fin, 0.15, r))
    return shadow_tint(m, (0.62, 0.50, 0.38))


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
CAM_HUB = dict(lens=100.0, elev=73.0, dist=0.45, az=-90.0, fstop=5.6, hub_px=(560, 1260))


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
    lamp_rig((0.0, 0.0), cam_az, key=4.5, rim=2.2)
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

def cams_report(names=None):
    """Build every asset's scene at its final size (no render) and print / save the compositor features (px in the
    asset's own frame; cropped assets also get frame_xy). Written to RWS/out/features_solve.json."""
    global SPILL
    _bpy()
    build_textures()
    out = {}
    for nm in (names or list(ASSETS)):
        A = ASSETS[nm]
        res = tuple(A['size'])
        MATS.clear()
        SPILL = None
        reset(res, 16)
        S = A['build'](res, 0.5)
        f = S['features']()
        if S.get('border'):
            b = S['border']
            f = dict(crop_rect_in_full_frame=b, crop_size=[b[2] - b[0], b[3] - b[1]], features_full_frame=f)
        out[nm] = dict(size=list(res), frames=A['n'], labels=A['labels'], features=f)
        print(nm, json.dumps(out[nm]), flush=True)
    os.makedirs(os.path.join(RWS, 'out'), exist_ok=True)
    with open(os.path.join(RWS, 'out', 'features_solve.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    return out




# ============================================================================= tubes + tape ribbons

def _sstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def resample(P, n=None, step=None):
    """Arc-length resample a polyline (n points, or one point per `step` metres)."""
    P = np.asarray(P, float)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    if n is None:
        n = max(2, int(math.ceil(s[-1] / step)) + 1)
    ss = np.linspace(0, s[-1], n)
    return np.stack([np.interp(ss, s, P[:, k]) for k in range(P.shape[1])], -1)


def catmull(P, n_per=24):
    """Centripetal-ish Catmull-Rom through control points P (k, d)."""
    P = np.asarray(P, float)
    Q = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    for i in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
        for t in np.linspace(0, 1, n_per, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-1])
    return np.asarray(out)


def ptf_frames(P, up=(0, 0, 1)):
    """Tangent + parallel-transport normal / binormal along P."""
    P = np.asarray(P, float)
    T = np.gradient(P, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
    up = np.asarray(up, float)
    N = np.zeros_like(P)
    n0 = up - T[0] * np.dot(up, T[0])
    if np.linalg.norm(n0) < 1e-6:
        n0 = np.array([1.0, 0, 0]) - T[0] * T[0][0]
    N[0] = n0 / np.linalg.norm(n0)
    for i in range(1, len(P)):
        n = N[i - 1] - T[i] * np.dot(N[i - 1], T[i])
        N[i] = n / max(np.linalg.norm(n), 1e-12)
    Bn = np.cross(T, N)
    return T, N, Bn


def tube(name, P, r, mat_, seg=12, step=None):
    """Round tube (cable) along P; r scalar or per-point array."""
    P = resample(P, step=step or max(0.0004, r * 0.8))
    T, N, Bn = ptf_frames(P)
    a = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    rr = np.broadcast_to(np.asarray(r, float), (len(P),)) if np.ndim(r) == 0 else np.interp(
        np.linspace(0, 1, len(P)), np.linspace(0, 1, len(r)), r)
    V3 = P[:, None, :] + rr[:, None, None] * (np.cos(a)[None, :, None] * N[:, None, :] +
                                              np.sin(a)[None, :, None] * Bn[:, None, :])
    o, _, _ = grid_mesh(name, V3, mat=mat_, cap0=tuple(P[0]), cap1=tuple(P[-1]))
    return o


def path2d(L, A, h0, turn, n):
    """2D path of length L from A with heading h0 + turn(u), u in [0, 1]."""
    u = np.linspace(0, 1, n)
    th = h0 + turn(u)
    ds = L / max(1, n - 1)
    d = np.stack([np.cos(th), np.sin(th)], -1)
    xy = np.asarray(A, float) + np.vstack([[0, 0], np.cumsum((d[:-1] + d[1:]) / 2 * ds, 0)])
    return u, xy, th


def curl_turn(base, curls, wig=(0.0, 0.0)):
    """Cumulative turning: base(u) + full 2 pi curls [(centre u, width u, sign)] + a gentle wiggle."""
    def f(u):
        t = base(u) + wig[0] * np.sin(2 * math.pi * 3.0 * u + wig[1])
        for c, w, s in curls:
            t = t + s * 2 * math.pi * _sstep((u - c + w / 2) / w)
        return t
    return f


def tape_mesh(name, P, U, mats, width=0.00381, accordion=(), seed=0, phase=0.0, stretched=None, parent=None):
    """Tape ribbon along centreline P (n, 3) with face normals U (n, 3). accordion = [(s0, s1, amp, period)] (metres
    along the tape): one-sided zig-zag folds along U; small random kinks everywhere; stretched = (s0, s1) gets the
    thinner, lighter material (index 2)."""
    P = np.asarray(P, float)
    U = np.asarray(U, float)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    T = np.gradient(P, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
    U = U - T * (U * T).sum(1, keepdims=True)
    U /= np.maximum(np.linalg.norm(U, axis=1, keepdims=True), 1e-12)
    rng = np.random.default_rng(seed)
    off = np.zeros(len(P))
    for (s0, s1, amp, per) in accordion:
        win = _sstep((s - s0) / 0.002) * _sstep((s1 - s) / 0.002)
        tri = np.abs(((s - s0) / per + phase) % 1.0 - 0.5) * 2.0
        jit = 1.0 + 0.35 * np.sin(s * 977.0 + seed)
        off += amp * tri * win * jit
    # kinks: sparse sharp bumps
    nk = max(1, int(s[-1] / 0.012))
    for _ in range(nk):
        c = rng.uniform(0, s[-1])
        off += rng.uniform(0.0002, 0.0006) * np.exp(-((s - c) / 0.0007) ** 2)
    P = P + U * off[:, None]
    Wd = np.cross(T, U)
    wid = np.full(len(P), width)
    mat_idx = None
    if stretched is not None:
        st = _sstep((s - stretched[0]) / 0.003) * _sstep((stretched[1] - s) / 0.003)
        wid = width * (1.0 - 0.18 * st)
        mat_idx = (st[:-1] + st[1:]) / 2 > 0.5
    Pw = P
    V = np.concatenate([Pw - Wd * wid[:, None] / 2, Pw + Wd * wid[:, None] / 2], 0)
    n = len(P)
    F = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
    uvs = np.stack([np.concatenate([s, s]) / max(s[-1], 1e-9), np.concatenate([np.zeros(n), np.ones(n)])], -1)
    o = B.mesh_from(name, V, F, None, uv=uvs, smooth=True)
    for m in mats:
        o.data.materials.append(m)
    if mat_idx is not None:
        o.data.polygons.foreach_set('material_index', np.where(mat_idx, 2, 0).astype(np.int32))
    sm = o.modifiers.new('solid', 'SOLIDIFY')
    sm.thickness = 0.00005
    sm.offset = 0.0
    sm.material_offset = 1
    sm.use_even_offset = True
    if parent is not None:
        o.parent = parent
    return o


def desk_tape(xy, th, phi, width=0.00381, lift=0.00004):
    """2D desk path -> (P, U): phi = 0 tape on its edge, pi/2 lying flat (face up)."""
    n2 = np.stack([-np.sin(th), np.cos(th), np.zeros_like(th)], -1)
    z = np.array([0.0, 0.0, 1.0])
    U = np.cos(phi)[:, None] * n2 + np.sin(phi)[:, None] * z
    T = np.stack([np.cos(th), np.sin(th), np.zeros_like(th)], -1)
    Wd = np.cross(T, U)
    h = 0.5 * width * np.abs(Wd[:, 2]) + lift + 0.5 * 0.00005 * np.abs(U[:, 2])
    P = np.column_stack([xy, h])
    return P, U


TAPE_MATS = ('tape_front', 'tape_back', 'tape_stretched', 'tape_back')

# The pulled-out loop (R1b), cassette local, relative to the centre head opening (0, -C_HY, C_T / 2), metres at
# scale 1: out of the opening on edge, it twists flat over the front edge and flops back onto the lower label in a
# crinkled, springy loop (parts lifted off the paper), so CAM_HUB sees it dark against the lit label.
RESCUE_A = np.array([-0.0034, 0.0030, 0.0])
RESCUE_B = np.array([0.0034, 0.0030, 0.0])
RESCUE_CTRL = np.array([(-0.0040, -0.0025, 0.0003), (-0.0070, -0.0050, 0.0035), (-0.0100, -0.0035, 0.0070),
                        (-0.0140, 0.0040, 0.0072), (-0.0150, 0.0120, 0.0090), (-0.0090, 0.0190, 0.0082),
                        (0.0000, 0.0210, 0.0098), (0.0090, 0.0180, 0.0076), (0.0140, 0.0100, 0.0071),
                        (0.0120, 0.0030, 0.0076), (0.0080, -0.0035, 0.0068), (0.0050, -0.0045, 0.0030),
                        (0.0040, -0.0025, 0.0003)])
RESCUE_TOP = C_T / 2 + 0.00035          # lowest z of tape lying on the shell face, relative to the opening centre


def _rescue_centreline(sc_):
    """Loop centreline at scale sc_ (x, y scaled; heights kept; tape over the shell face kept above it)."""
    O = np.array([0.0, -C_HY, C_T / 2])
    C = RESCUE_CTRL.copy()
    C[:, :2] *= sc_
    C[:, 2] *= min(1.0, 0.35 + sc_)
    P = catmull(np.vstack([RESCUE_A, C, RESCUE_B]), 24)
    in_opening = (np.abs(P[:, 0]) < 0.0045) & (P[:, 1] < 0.0045)
    over_face = (P[:, 1] > 0.0005) & ~in_opening
    P[over_face, 2] = np.maximum(P[over_face, 2], RESCUE_TOP)
    return P + O


def rescue_tape(L, parent, frame=0):
    """The crinkled tape loop out of the centre head opening (cassette local), length L (m); None when L ~ 0.
    The loop's footprint is scaled so its arc length is L: it withdraws into the opening as the pencil rewinds."""
    if L < 0.002:
        return None
    lo, hi = 0.0, 4.0
    for _ in range(30):                         # bisection on the scale for arc length L
        mid = (lo + hi) / 2
        P = _rescue_centreline(mid)
        Lm = np.linalg.norm(np.diff(P, axis=0), axis=1).sum()
        lo, hi = (mid, hi) if Lm < L else (lo, mid)
    P = resample(_rescue_centreline((lo + hi) / 2), step=0.00022)
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    Ls = s[-1]
    T = np.gradient(P, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
    # width: z (on edge) through the opening, horizontal (lying flat, face up) over the shell, a wandering twist
    w = _sstep(s / 0.007) * _sstep((Ls - s) / 0.007)
    flat = np.cross(np.array([0.0, 0.0, 1.0])[None, :], T)
    flat /= np.maximum(np.linalg.norm(flat, axis=1, keepdims=True), 1e-9)
    Wd = np.array([0.0, 0.0, 1.0])[None, :] * (1 - w)[:, None] + flat * w[:, None]
    Wd = Wd - T * (Wd * T).sum(1, keepdims=True)
    Wd /= np.maximum(np.linalg.norm(Wd, axis=1, keepdims=True), 1e-12)
    lifted = np.clip((P[:, 2] - (C_T + 0.0012)) / 0.002, 0, 1)            # twist only where it is off the paper
    tw = w * lifted * np.radians(50.0) * np.sin(2 * math.pi * (s / max(Ls, 1e-6)) * 2.0 + 0.7)
    Nn = np.cross(T, Wd)
    Wd = Wd * np.cos(tw)[:, None] + Nn * np.sin(tw)[:, None]
    U = np.cross(Wd, T)
    U = np.where((U[:, 2:3] < 0) & (w[:, None] > 0.5), -U, U)               # face normal up: crinkles lift
    acc = [(Ls * 0.30, Ls * 0.30 + min(0.026, Ls * 0.22), 0.0010, 0.0013),
           (Ls * 0.62, Ls * 0.62 + min(0.014, Ls * 0.12), 0.0007, 0.0011)]
    return tape_mesh('rescue_tape', P, U, [mat(m) for m in TAPE_MATS], accordion=acc, seed=3, phase=0.0,
                     stretched=(Ls * 0.50, Ls * 0.50 + min(0.012, Ls * 0.1)) if Ls > 0.03 else None, parent=parent)


# ============================================================================= WALKMAN, HEADPHONES, BATTERIES

W_ZT = W_T - W_LID['t']                       # body top (lid sits on it)
W_COMP = dict(cy=W_CASS[1], hx=0.0512, hy=0.0329, z0=0.0140)
W_JACK = (-W_HX, -0.020, 0.0120)
W_WHEEL = (-W_HX + 0.0082, 0.022, 0.0140, 0.0110)   # centre x, y, z, radius


def _walk_body_fn(P):
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    zt = W_ZT
    r = 0.0009
    outer = B.extrude(B.sd_rect(x, y, W_HX, W_HY, 0.0042) + r, np.abs(z - zt / 2) - zt / 2 + r) - r
    cz0, cz1 = W_COMP['z0'], zt + 0.003
    comp = B.extrude(B.sd_rect(x, y - W_COMP['cy'], W_COMP['hx'], W_COMP['hy'], 0.0030),
                     np.abs(z - (cz0 + cz1) / 2) - (cz1 - cz0) / 2)
    d = B.smax(outer, -comp, 0.0005)
    for kx in W_KEY_X:
        slot = B.extrude(B.sd_rect(x - kx, y - W_KEY_Y, W_KEY_W / 2 + 0.00035, W_KEY_D / 2 + 0.00035, 0.0011),
                         np.abs(z - zt) - 0.0045)
        d = B.smax(d, -slot, 0.0003)
    led = B.extrude(np.hypot(x - W_LED[0], y - W_LED[1]) - 0.00125, np.abs(z - zt) - 0.0012)
    d = B.smax(d, -led, 0.0002)
    # shell seam groove all round (two-part housing)
    cut = np.maximum(np.abs(z - 0.0100) - 0.00022, -outer - 0.0004)
    d = np.maximum(d, -cut)
    # headphone jack + volume-wheel slot on the left side
    jack = np.maximum(np.hypot(y - W_JACK[1], z - W_JACK[2]) - 0.0019, np.abs(x - W_JACK[0]) - 0.007)
    d = B.smax(d, -jack, 0.0003)
    wx, wy, wz, wr = W_WHEEL
    slot = np.maximum(np.maximum(np.abs(y - wy) - 0.0105, np.abs(z - wz) - 0.0029), np.abs(x + W_HX) - 0.0045)
    d = B.smax(d, -slot, 0.0003)
    # three short vent slots on the front face, right of centre
    for vx in (0.006, 0.012, 0.018):
        v = np.maximum(np.maximum(np.abs(x - vx) - 0.0006, np.abs(z - 0.0055) - 0.0026), np.abs(y + W_HY) - 0.0008)
        d = B.smax(d, -v, 0.0002)
    return d


L_LEN = W_LID['x1'] - W_LID['x0']


def _lid_fn(P):
    """Lid in hinge coords: x 0 .. L_LEN from the hinge line, y world, z 0 .. t."""
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    t = W_LID['t']
    cy = (W_LID['y0'] + W_LID['y1']) / 2
    hy = (W_LID['y1'] - W_LID['y0']) / 2
    r = 0.0005
    plate = B.extrude(B.sd_rect(x - L_LEN / 2, y - cy, L_LEN / 2, hy, 0.0036) + r, np.abs(z - t / 2) - t / 2 + r) - r
    wx = W_WIN[0] - W_LID['x0']
    hole = B.sd_rect(x - wx, y - W_WIN[1], W_WIN[2], W_WIN[3], 0.0030)
    chamfer = hole + (z - t) * 0.8           # widening towards the top face
    d = B.smax(plate, -np.minimum(hole, chamfer), 0.0003)
    # finger grip ribs near the free (right) edge
    for k in range(4):
        gx = L_LEN - 0.0045 - k * 0.0016
        rib = B.extrude(B.sd_rect(x - gx, y - cy, 0.00035, 0.010, 0.0002), np.abs(z - t) - 0.00018)
        d = np.maximum(d, -rib)
    return d


def _key_fn(P):
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    r = 0.0006
    z0, z1 = -0.0045, W_KEY_UP
    dish = 0.00018 * (1 - (x / (W_KEY_W / 2)) ** 2)
    zz = z + np.where(z > 0, dish, 0)
    return B.extrude(B.sd_rect(x, y, W_KEY_W / 2, W_KEY_D / 2, 0.0010) + r,
                     np.abs(zz - (z0 + z1) / 2) - (z1 - z0) / 2 + r) - r


def build_walkman(name='walk', q=1.0, lid_deg=0.0, keys_down=(), led_on=True):
    root = empty(name)
    st = 0.00020 if q >= 1 else 0.00034
    body, V, Q = sdf_obj(f'{name}_body', _walk_body_fn, (-W_HX - 0.001, -W_HY - 0.001, -0.001),
                         (W_HX + 0.001, W_HY + 0.001, W_ZT + 0.001), st, mat('abs'), 'walk_body1')
    lid_root = empty(f'{name}_lidroot', loc=(W_LID['x0'], 0.0, W_ZT), parent=root)
    lid_root.rotation_euler = (0, -math.radians(lid_deg), 0)
    lid, _, _ = sdf_obj(f'{name}_lid', _lid_fn, (-0.001, W_LID['y0'] - 0.001, -0.001),
                        (L_LEN + 0.001, W_LID['y1'] + 0.001, W_LID['t'] + 0.001),
                        0.00012 if q >= 1 else 0.0002, mat('alu'), 'walk_lid1')
    lid.parent = lid_root
    glass = B.cube(f'{name}_glass', (W_WIN[0] - W_LID['x0'] - W_WIN[2] - 0.0008, W_WIN[1] - W_WIN[3] - 0.0008, 0.0002),
                   (W_WIN[0] - W_LID['x0'] + W_WIN[2] + 0.0008, W_WIN[1] + W_WIN[3] + 0.0008, 0.0010),
                   mat('smoke'), bevel=0.0003)
    glass.parent = lid_root
    hinge = B.cyl(f'{name}_hinge', (0.0, (W_LID['y0'] + W_LID['y1']) / 2, 0.0002), 0.0011,
                  (W_LID['y1'] - W_LID['y0']) - 0.016, mat('chrome'), axis='Y', seg=24)
    hinge.parent = lid_root
    # cassette in the compartment, side A up, head edge to the front
    C = build_cassette(f'{name}_cass', rL=0.0185, rR=0.0190, parent=root, q=q)
    C['root'].location = W_CASS
    # keys
    kV, kQ, kN = H.mesh_field(H.FieldFn(_key_fn, (-W_KEY_W / 2 - 0.0005, -W_KEY_D / 2 - 0.0005, -0.0047),
                                        (W_KEY_W / 2 + 0.0005, W_KEY_D / 2 + 0.0005, W_KEY_UP + 0.0003)),
                              0.00007 if q >= 1 else 0.00011, cache_key=f'{REEL}:key1:{q >= 1}')
    keys = {}
    for nm, kx in zip(W_KEYS, W_KEY_X):
        ko = H.add_mesh(f'{name}_key_{nm}', kV, kQ, kN, mat(f'key_{nm}'), icon_frame=False)
        ko.location = (kx, W_KEY_Y, W_ZT - (0.0030 if nm in keys_down else 0.0))
        ko.parent = root
        keys[nm] = ko
    led = B.lathe if False else None
    lp = [(0.0, 0.00075), (0.0005, 0.00068), (0.0009, 0.0004), (0.00105, 0.0), (0.00105, -0.001), (0.0, -0.001)]
    led = lathe_mesh(f'{name}_led', lp, 32, mat('led' if led_on else 'led_off'))
    led.location = (W_LED[0], W_LED[1], W_ZT - 0.0002)
    led.parent = root
    # volume wheel (axis Z), ribbed rim protruding from the left side slot
    wx, wy, wz, wr = W_WHEEL
    wp = [(0.0, -0.0022), (wr - 0.0004, -0.0022), (wr, -0.0018), (wr, 0.0018), (wr - 0.0004, 0.0022), (0.0, 0.0022)]

    def ribs(V3f, a):
        rr = np.hypot(V3f[..., 0], V3f[..., 1])
        k = 1.0 - 0.00028 / wr * (np.cos(a * 72.0)[None, :] > 0.2) * (rr > wr - 0.0005)
        V3f[..., 0] *= k
        V3f[..., 1] *= k
        return V3f
    wheel = lathe_mesh(f'{name}_wheel', wp, 288, mat('rubber'), disp=ribs, smooth=False)
    wheel.location = (wx, wy, wz)
    wheel.parent = root
    # jack ring + headphone plug + strain relief
    jr = lathe_mesh(f'{name}_jackring', [(0.0019, -0.0004), (0.0026, -0.0004), (0.0027, 0.0), (0.0026, 0.0004),
                                         (0.0019, 0.0004)], 48, mat('nickel'))
    jr.rotation_euler = (0, math.radians(-90), 0)
    jr.location = (W_JACK[0] - 0.0002, W_JACK[1], W_JACK[2])
    jr.parent = root
    plug = lathe_mesh(f'{name}_plug', [(0.0, 0.0), (0.0017, 0.0), (0.0017, 0.0008), (0.0029, 0.0012),
                                       (0.0030, 0.0090), (0.0024, 0.0115), (0.0017, 0.0170), (0.0012, 0.0180),
                                       (0.0, 0.0182)], 40, mat('rubber'))
    plug.rotation_euler = (0, math.radians(-90), 0)
    plug.location = (W_JACK[0] - 0.0004, W_JACK[1], W_JACK[2])
    plug.parent = root
    parent_to([body], root)
    return dict(root=root, lid_root=lid_root, C=C, keys=keys, led=led, body=body, lid=lid,
                plug_end=(W_JACK[0] - 0.0004 - 0.0180, W_JACK[1], W_JACK[2]))


def build_headphones(name, center, yaw, cable_to=None, q=1.0, seed=5):
    """Lying on the desk pads up: semicircular chrome band (span 140 mm) on the desk, two cups (45 mm) with
    orange foam pads (one torn), a tangled cable towards `cable_to` (world point)."""
    root = empty(name, loc=(center[0], center[1], 0.0), rot=(0, 0, yaw))
    R = 0.070
    objs = []
    # band: flat strip 3.2 x 0.8 mm on edge, lifted 6 mm at the crown
    a = np.linspace(math.radians(8), math.radians(172), 120)
    P = np.stack([R * np.cos(a), R * np.sin(a) * 0.82, 0.0045 + 0.004 * np.sin(a) ** 2], -1)
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    nrm = np.cross(T, [0, 0, 1.0])
    V3 = []
    for (dx, dz) in ((-0.0004, -0.0016), (0.0004, -0.0016), (0.0004, 0.0016), (-0.0004, 0.0016)):
        V3.append(P + nrm * dx + np.array([0, 0, dz]))
    V3 = np.stack(V3, 1)
    band, _, _ = grid_mesh(f'{name}_band', V3, mat=mat('chrome'), smooth=True)
    sm = band.modifiers.new('bev', 'BEVEL')
    sm.width = 0.0002
    sm.segments = 2
    objs.append(band)
    # yoke sliders down to the cups
    for side in (-1, 1):
        cx = side * (R + 0.006)
        cyl = B.cyl(f'{name}_slider{side}', (side * R * 0.99, 0.004, 0.0045), 0.0012, 0.016, mat('cup'), axis='Y',
                    seg=16)
        objs.append(cyl)
        cup = lathe_mesh(f'{name}_cup{side}', [(0.0, 0.0002), (0.0200, 0.0002), (0.0222, 0.0012), (0.0225, 0.0080),
                                               (0.0215, 0.0098), (0.0, 0.0098)], 96, mat('cup'))
        cup.location = (cx, -0.012, 0.0)
        objs.append(cup)
        grill = B.cyl(f'{name}_grill{side}', (cx, -0.012, 0.0099), 0.0150, 0.0003, mat('chrome'), seg=64)
        objs.append(grill)
        torn = side > 0

        def pad_disp(V3f, aa, torn=torn):
            if torn:
                rr = np.hypot(V3f[..., 0], V3f[..., 1])
                cut = np.exp(-((aa[None, :] - 0.9) / 0.18) ** 2) * (rr > 0.019)
                k = 1.0 - 0.10 * cut
                V3f[..., 0] *= k
                V3f[..., 1] *= k
                V3f[..., 2] -= 0.0025 * cut
            # hand-cut foam is never a perfect lathe: low-frequency lumps in the outline and the top
            rr = np.hypot(V3f[..., 0], V3f[..., 1])
            a2 = aa[None, :]
            k = 1.0 + 0.012 * np.sin(2 * a2 + 1.3 * side) + 0.007 * np.sin(5 * a2 + 0.4)
            V3f[..., 0] *= k
            V3f[..., 1] *= k
            V3f[..., 2] += 0.00045 * np.sin(3 * a2 + side) * np.clip(rr / 0.025, 0, 1) * (V3f[..., 2] > 0.012)
            return V3f
        # flat open-cell foam disc 50 x 10 mm over the driver (no hole), soft rolled edge, slightly sagging centre
        pr = [(0.0, 0.0188), (0.0060, 0.0189), (0.0120, 0.0192), (0.0170, 0.0194), (0.0205, 0.0191),
              (0.0230, 0.0181), (0.0246, 0.0163), (0.0251, 0.0140), (0.0248, 0.0115), (0.0236, 0.0100),
              (0.0215, 0.0098)]
        pad = lathe_mesh(f'{name}_pad{side}', pr, 128, mat('foam'), disp=pad_disp)
        pad.location = (cx, -0.012, 0.0)
        objs.append(pad)
    parent_to(objs, root)
    cab = None
    if cable_to is not None:
        bpy.context.view_layer.update()
        start = wpos(root, (-(R + 0.006) - 0.020, -0.012, 0.004))
        end = np.asarray(cable_to, float)
        rng = np.random.default_rng(seed)
        ctrl = [start]
        k = 9
        for i in range(1, k):
            t = i / k
            p = start * (1 - t) + end * t
            p = p + np.array([rng.normal(0, 0.018), rng.normal(0, 0.018), 0.0])
            p[2] = 0.0011 + (0.004 if i % 3 == 1 else 0.0)
            ctrl.append(p)
        ctrl.append(end)
        Pc = catmull(np.asarray(ctrl), 30)
        # a couple of loops (tangle)
        loops = []
        for li, (pos, rad) in enumerate(((0.35, 0.011), (0.62, 0.008))):
            i0 = int(pos * len(Pc))
            c0 = Pc[i0]
            aa = np.linspace(0, 2 * np.pi, 60)
            loops.append((i0, c0 + np.stack([rad * np.sin(aa), rad * (1 - np.cos(aa)), 0.0016 * np.sin(aa / 2)], -1)))
        Pl = []
        last = 0
        for i0, lp in loops:
            Pl.append(Pc[last:i0])
            Pl.append(lp)
            last = i0 + 1
        Pl.append(Pc[last:])
        Pc = np.vstack(Pl)
        Pc[:, 2] = np.maximum(Pc[:, 2], 0.0010)
        cab = tube(f'{name}_cable', Pc, 0.0010, mat('cable'), seg=10)
    return dict(root=root, objs=objs, cable=cab)


def build_battery(name, loc, yaw, roll=0.0, dented=False):
    """AA cell lying on the desk: sleeve (UV unwrap of tex_battery), nickel + cap and - disc; dented: 3 tooth dents
    mid-sleeve with a wrinkled sleeve."""
    root = empty(name, loc=(loc[0], loc[1], 0.00725), rot=(0, math.radians(90), yaw))
    Rb = 0.00725
    L = 0.0493
    prof = [(Rb - 0.0004, 0.0003), (Rb - 0.00005, 0.0005), (Rb, 0.0009)] + \
           [(Rb, z) for z in np.linspace(0.0012, L - 0.0012, 90)] + [(Rb, L - 0.0009), (Rb - 0.00005, L - 0.0005),
                                                                   (Rb - 0.0004, L - 0.0003)]

    def dents(V3f, a):
        if not dented:
            return V3f
        z = V3f[..., 2]
        dep = np.zeros(z.shape)
        for (ac, zc) in ((0.0, 0.024), (0.35, 0.0265), (-0.30, 0.0218)):
            da = np.angle(np.exp(1j * (a[None, :] - ac)))
            dep += 0.00042 * np.exp(-(da / 0.10) ** 2 - ((z - zc) / 0.0011) ** 2)
            dep += 0.00006 * np.sin((z - zc) * 4200.0) * np.exp(-(da / 0.35) ** 2 - ((z - zc) / 0.004) ** 2)
        k = (Rb - dep) / Rb
        V3f[..., 0] *= k
        V3f[..., 1] *= k
        return V3f
    sl = lathe_mesh(f'{name}_sleeve', prof, 128, mat('sleeve'), disp=dents, uv=True)
    sl.rotation_euler = (0, 0, roll)
    neg = lathe_mesh(f'{name}_neg', [(0.0, -0.00005), (0.0055, -0.00005), (Rb - 0.0004, 0.0003), (0.0, 0.0003)], 48,
                     mat('nickel'))
    pos = lathe_mesh(f'{name}_pos', [(0.0, L + 0.0012), (0.0024, L + 0.0012), (0.0027, L + 0.0009),
                                     (0.0027, L - 0.0003), (Rb - 0.0004, L - 0.0003), (0.0, L - 0.0003)], 48,
                     mat('nickel'))
    for o in (sl, neg, pos):
        o.location = (0, 0, -L / 2)
    parent_to([sl, neg, pos], root)
    return root


# ============================================================================= walkman spill (R4b)

# out of the centre head opening (cassette head edge faces the key strip), up over the compartment rim under the
# raised free edge of the lid, across the front strip between the REW key and the LED, down the front face (towards
# CAM_WALK) and onto the desk, where it curls in front of the player towards screen left (clear of the AA cells).
SPILL_CTRL = np.array([(0.000, -0.0255, 0.0210), (0.006, -0.0262, 0.0238), (0.016, -0.0268, 0.0290),
                       (0.0250, -0.0290, 0.0316), (0.0275, -0.0345, 0.0302), (0.0278, -0.0394, 0.0290),
                       (0.0280, -0.0418, 0.0236), (0.0282, -0.0421, 0.0120), (0.0284, -0.0430, 0.0040),
                       (0.0280, -0.0470, 0.0012)])
SPILL_U = np.array([(0, -1, 0), (0, -1, 0.3), (0, -0.5, 1), (0, 0, 1), (0, -0.2, 1), (0, -1, 0.7), (0, -1, 0),
                    (0, -1, 0.05), (0, -1, 0.3), (0, -0.3, 1)], float)
SPILL_DESK_L = 0.175
SPILL_TURN = curl_turn(lambda u: -1.45 * _sstep(u / 0.10) - 0.30 * u,
                       [(0.22, 0.21, 1), (0.50, 0.19, -1), (0.80, 0.20, 1)], wig=(0.30, 0.4))


def spill_path():
    """Full spill centreline + face normals (walkman local, lid open): out of the head opening, over the lid lip /
    front strip, down the front face, then three crinkled curls on the desk."""
    P1 = catmull(SPILL_CTRL, 30)
    U1 = catmull(SPILL_U, 30)
    P1 = resample(P1, step=0.00025)
    U1 = resample(U1 / np.linalg.norm(U1, axis=1, keepdims=True), n=len(P1))
    n2 = max(300, int(SPILL_DESK_L / 0.00025))
    h0 = math.atan2(SPILL_CTRL[-1][1] - SPILL_CTRL[-2][1], SPILL_CTRL[-1][0] - SPILL_CTRL[-2][0])
    u, xy, th = path2d(SPILL_DESK_L, SPILL_CTRL[-1][:2], h0, SPILL_TURN, n2)
    phi = np.radians(90.0) * (1 - _sstep(u / 0.12)) + np.radians(25.0) * _sstep(u / 0.12) * \
        (1.0 + 0.6 * np.sin(u * 17.0)) + np.radians(50.0) * _sstep((u - 0.92) / 0.08)
    P2, U2 = desk_tape(xy, th, phi)
    P = np.vstack([P1, P2[1:]])
    U = np.vstack([U1, U2[1:]])
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    return P, U, s


SPILL = None


def spill_tape(frac, frame, parent):
    """The first `frac` of the spill path (tip leading), crinkle animated with the frame."""
    global SPILL
    if SPILL is None:
        SPILL = spill_path()
    P, U, s = SPILL
    Lv = frac * s[-1]
    if Lv < 0.002:
        return None
    k = int(np.searchsorted(s, Lv)) + 1
    P, U = P[:k].copy(), U[:k].copy()
    L1 = len(resample(catmull(SPILL_CTRL, 30), step=0.00025)) * 0.00025
    acc = [(L1 + 0.050, L1 + 0.082, 0.0012, 0.0014), (L1 + 0.120, L1 + 0.140, 0.0009, 0.0011)]
    # the free tip still flutters while it moves
    tip = _sstep((np.arange(k) - (k - 60)) / 60.0)
    P[:, 2] += 0.0025 * tip * (1.0 - frac) * (0.6 + 0.4 * math.sin(frame * 1.7))
    return tape_mesh('spill_tape', P, U, [mat(m) for m in TAPE_MATS], accordion=acc, seed=11, phase=0.04 * frame,
                     stretched=(L1 + 0.022, L1 + 0.034), parent=parent)


# ============================================================================= scenes (continued)

CAM_LABEL = dict(lens=60.0, dist=0.33, fstop=5.6, yaw=6.0, label_px=(540, 900))
CAM_WALK = dict(lens=50.0, elev=30.0, az=-122.0, dist=0.40, fstop=8.0, px=(540, 1180), width_px=760)
WALK_YAW = math.radians(0.0)
LID_OPEN = [0.0, 9.0, 19.0, 26.0, 24.0, 22.0]


def lying_pencil(name, tip_xy, ang_deg, q):
    """Pencil lying on the desk on a flat, HB facet up, tip at tip_xy, axis (tip -> eraser) at ang_deg."""
    holder = empty(f'{name}_lie', loc=(tip_xy[0], tip_xy[1], 0.00372),
                   rot=(-math.pi / 2, 0.0, math.radians(ang_deg - 90.0)))
    Pn = build_pencil(name, parent=holder, q=q)
    Pn['root'].rotation_euler = (0, 0, -math.pi / 2)
    Pn['holder'] = holder
    return Pn


def scene_label(res, q):
    C = build_cassette('cass', rL=0.017, rR=0.0204, q=q)
    C['root'].rotation_euler = (0, 0, math.radians(CAM_LABEL['yaw']))
    Pn = lying_pencil('pencil', (-0.030, -0.0405), -14.0, q)
    build_desk(center=(0, 0), wall_dist=0.9, wall_dir=(0, 1), front=0.20)

    def avoid(x, y):
        return abs(x) < C_HX + 0.003 and abs(y) < C_HY + 0.003
    build_crumbs(18 if q >= 1 else 8, (0.0, -0.01), 0.04, 0.07, 9, avoid=avoid, ang_range=(180, 360))
    bpy.context.view_layer.update()
    lamp_rig((0.0, 0.0), math.radians(-90), key=4.0, rim=1.6, key_side=0.18, key_back=-0.05, key_h=0.42)
    lc = wpos(C['root'], ((LAB_X0 + LAB_X1) / 2, (LAB_Y0 + LAB_Y1) / 2, C_T))
    cam = make_cam(res, CAM_LABEL['lens'], lc, math.radians(90), math.radians(-90), CAM_LABEL['dist'],
                   px=tuple(v * res[0] / 1080.0 for v in CAM_LABEL['label_px']), fstop=CAM_LABEL['fstop'], focus=lc)
    return dict(C=C, P=Pn, cam=cam)


def label_features(S):
    C, Pn = S['C'], S['P']
    s = 1.0
    q = [proj_px(wpos(C['root'], (x, y, C_T))) for x, y in ((LAB_X0, LAB_Y1), (LAB_X1, LAB_Y1), (LAB_X1, LAB_Y0),
                                                            (LAB_X0, LAB_Y0))]
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    f = dict(label_quad=q, label_rect=[min(xs), min(ys), max(xs), max(ys)],
             cassette_quad=[proj_px(wpos(C['root'], (x * C_HX, y * C_HY, C_T))) for x, y in
                            ((-1, 1), (1, 1), (1, -1), (-1, -1))],
             pencil_tip=proj_px(wpos(Pn['root'], (0, 0, 0))), pencil_eraser=proj_px(wpos(Pn['root'], (0, 0, P_LEN))))
    return {k: np.round(np.asarray(v, float) * s, 1).tolist() for k, v in f.items()}


def desk_point(px, res, z=0.0):
    """World point on the plane z = `z` seen at pixel px (x right, y down) of the scene camera."""
    sc = bpy.context.scene
    cam = sc.camera
    fr = [cam.matrix_world @ v for v in cam.data.view_frame(scene=sc)]      # TR, BR, BL, TL (world)
    tr, br, bl, tl = [np.asarray(v, float) for v in fr]
    u, v = px[0] / res[0], px[1] / res[1]
    p = tl + (tr - tl) * u + (bl - tl) * v
    o = np.asarray(cam.matrix_world.translation, float)
    if cam.data.type == 'ORTHO':
        d = np.asarray(cam.matrix_world.to_3x3() @ Vector((0, 0, -1)), float)
        o = p
    else:
        d = p - o
    t = (z - o[2]) / d[2]
    return o + d * t


WALK_PADS_PX = (260, 1000)          # torn pad centre (SHOTS.md CAM_WALK), 1080-wide frame px
WALK_AA_PX = (790, 1630)            # dented AA centre (SHOTS.md ~(820, 1500); moved down to clear the R4b spill)


def scene_walk(res, q, lid_deg=0.0, keys_down=(), led_on=True):
    Wk = build_walkman('walk', q=q, lid_deg=lid_deg, keys_down=keys_down, led_on=led_on)
    Wk['root'].rotation_euler = (0, 0, WALK_YAW)
    bpy.context.view_layer.update()
    cam_az = math.radians(CAM_WALK['az'])
    tgt = wpos(Wk['root'], (0.0, -0.004, W_T * 0.75))
    k = res[0] / 1080.0
    cam = make_cam(res, CAM_WALK['lens'], tgt, math.radians(CAM_WALK['elev']), cam_az, CAM_WALK['dist'],
                   px=tuple(v * k for v in CAM_WALK['px']), fstop=CAM_WALK['fstop'],
                   focus=wpos(Wk['root'], (0.0, -0.012, W_T)))
    bpy.context.view_layer.update()
    plug_end = wpos(Wk['root'], Wk['plug_end'])
    # headphones: torn pad (cup +1) at WALK_PADS_PX, band arcing away from camera, the other cup off frame left
    yaw_h = cam_az + math.pi / 2          # band (local +y) points away from the camera; cup +1 to screen right
    pad = desk_point(tuple(v * k for v in WALK_PADS_PX), res)
    off = np.array([math.cos(yaw_h) * 0.076 - math.sin(yaw_h) * -0.012, math.sin(yaw_h) * 0.076 + math.cos(yaw_h) * -0.012])
    Hp = build_headphones('phones', tuple(pad[:2] - off), yaw_h, cable_to=plug_end, q=q)
    aa = desk_point(tuple(v * k for v in WALK_AA_PX), res, z=0.00725)
    build_battery('aa1', (aa[0], aa[1]), cam_az + math.radians(70.0), roll=math.pi, dented=True)
    y1 = cam_az + math.radians(70.0)                    # dented cell axis; the second cell lies beside it,
    side = np.array([math.cos(y1 - math.pi / 2), math.sin(y1 - math.pi / 2)])   # on the side away from the spill
    a2 = aa[:2] + side * 0.0158 + np.array([math.cos(y1), math.sin(y1)]) * 0.009
    build_battery('aa2', (a2[0], a2[1]), y1 + math.radians(7.0), roll=0.6, dented=False)
    build_desk(center=(0, 0), wall_dist=0.9, wall_dir=(0, 1), front=0.25)

    def avoid(x, y):
        return (abs(x) < W_HX + 0.004 and abs(y) < W_HY + 0.004) or math.hypot(x - aa[0], y - aa[1]) < 0.04
    build_crumbs(16 if q >= 1 else 8, (-0.02, -0.06), 0.01, 0.05, 12, avoid=avoid, ang_range=(190, 300))
    bpy.context.view_layer.update()
    lamp_rig((0.0, 0.0), cam_az, key=8.0, rim=1.4, bounce=0.7, key_side=0.22, key_back=0.06, key_h=0.45)
    print('[walk] aa world', np.round(aa, 4).tolist(), 'pad world', np.round(pad, 4).tolist(), flush=True)
    return dict(W=Wk, Hp=Hp, cam=cam, aa_xy=tuple(aa[:2]), pad_xy=tuple(pad[:2]))


def walk_features(S):
    Wk = S['W']
    lr = Wk['lid_root']
    wx = W_WIN[0] - W_LID['x0']
    win = [proj_px(wpos(lr, (wx + sx * W_WIN[2], W_WIN[1] + sy * W_WIN[3], W_LID['t'])))
           for sx, sy in ((-1, 1), (1, 1), (1, -1), (-1, -1))]
    keys = {}
    for nm, ko in Wk['keys'].items():
        q = [proj_px(wpos(ko, (sx * W_KEY_W / 2, sy * W_KEY_D / 2, W_KEY_UP))) for sx, sy in
             ((-1, 1), (1, 1), (1, -1), (-1, -1))]
        keys[nm] = [min(p[0] for p in q), min(p[1] for p in q), max(p[0] for p in q), max(p[1] for p in q)]
    xs, ys = [p[0] for p in win], [p[1] for p in win]
    body = [proj_px(wpos(Wk['root'], (sx * W_HX, sy * W_HY, sz))) for sx in (-1, 1) for sy in (-1, 1)
            for sz in (0.0, W_T)]
    f = dict(window_quad=win, window_rect=[min(xs), min(ys), max(xs), max(ys)], key_rects=keys,
             led_xy=proj_px(wpos(Wk['root'], (W_LED[0], W_LED[1], W_ZT + 0.0007))),
             hub_l_xy=proj_px(wpos(Wk['C']['hubL'], (0, 0, C_T))), hub_r_xy=proj_px(wpos(Wk['C']['hubR'], (0, 0, C_T))),
             walkman_bbox=[min(p[0] for p in body), min(p[1] for p in body), max(p[0] for p in body),
                           max(p[1] for p in body)])
    if 'aa_xy' in S:
        f['battery_dented_xy'] = proj_px((S['aa_xy'][0], S['aa_xy'][1], 0.00725))
        f['torn_pad_xy'] = proj_px((S['pad_xy'][0], S['pad_xy'][1], 0.019))

    def rnd(v):
        if isinstance(v, dict):
            return {k: rnd(x) for k, x in v.items()}
        return np.round(np.asarray(v, float), 1).tolist()
    return rnd(f)


def scene_pencil_top(res, q):
    Pn = lying_pencil('pencil', (0.0, -P_LEN / 2), 90.0, q)
    plane = B.cube('catcher', (-0.15, -0.15, -0.001), (0.15, 0.15, 0.0), None)
    plane.is_shadow_catcher = True
    bpy.context.view_layer.update()
    rig = lamp_rig((0.0, 0.0), math.radians(-90), key=8.0, rim=1.2, bounce=0.5, key_side=0.16, key_back=-0.10,
                   key_h=0.45)
    rig['key'].data.spot_size = math.radians(110.0)      # even light along the whole 120 mm (no falloff in the shadow)
    rig['key'].data.spot_blend = 0.1
    rig['key'].data.color = mixl('LAMP', '#FFF1E0', 0.6)     # the cut-out sits on UI glass: keep the lacquer yellow
    ortho = P_LEN * ASSETS['pencil_top']['size'][1] / 1500.0     # 1500 px per pencil at any render scale
    cam = make_cam(res, 50.0, (0.0, 0.0, 0.0035), math.radians(90), math.radians(-90), 0.5, ortho=ortho)
    return dict(P=Pn, plane=plane, cam=cam, rig=rig)


def _keyframe_rot(obj, fn, f0, f1):
    """Keyframe obj.rotation_euler = fn(f) on every integer frame f0..f1 (collinear keys = linear motion)."""
    for f in range(f0, f1 + 1):
        obj.rotation_euler = fn(f)
        obj.keyframe_insert('rotation_euler', frame=f)


def _remove(o):
    if o is None:
        return
    me = o.data
    bpy.data.objects.remove(o, do_unlink=True)
    if me is not None and me.users == 0:
        bpy.data.meshes.remove(me)


# ============================================================================= render list

ASSETS = {}


def asset(name, size, spp, n, labels=None, notes='', mode='anim', loop=False, opaque=True, mb=True, gpu_spp=None):
    """Register a render. spp = CPU final samples (SHOTS.md budget), gpu_spp = final samples on a GPU
    (FOSTER_GPU=1, e.g. RTX 4060 OptiX); both with adaptive sampling + OIDN."""
    def deco(fn):
        ASSETS[name] = dict(name=name, size=size, spp=spp, n=n, labels=labels or [mode] * n, notes=notes, mode=mode,
                            loop=loop, opaque=opaque, mb=mb, build=fn, gpu_spp=gpu_spp or max(256, spp * 4))
        return fn
    return deco


def _spin_hubs(C, deg_per_frame, f0, f1, pencil_holder=None):
    for ho in (C['hubL'], C['hubR']):
        r0 = tuple(ho.rotation_euler)
        _keyframe_rot(ho, lambda f, r0=r0: (r0[0], r0[1], r0[2] + math.radians(deg_per_frame * f)), f0, f1)


@asset('hub_loop', (1080, 1920), 64, 16, notes='R1: pencil + both hubs turn clockwise (rewind, side A) 22.5 deg/f = '
       '1 rev per beat (16 f); frame 16 == frame 0; idx = f mod 16', mode='loop', loop=True, gpu_spp=384)
def build_hub_loop(res, q):
    S = scene_hub(res, q)
    _spin_hubs(S['C'], -22.5, -2, 18)
    sc = bpy.context.scene

    def update(i):
        sc.frame_set(i)
    return dict(update=update, features=lambda: hub_features(S))


@asset('hub_cover', (1080, 1920), 192, 1, labels=['cover'], notes='still = hub_loop frame 0 at high spp',
       mode='static', mb=False, gpu_spp=1024)
def build_hub_cover(res, q):
    S = scene_hub(res, q)
    return dict(update=lambda i: bpy.context.scene.frame_set(0), features=lambda: hub_features(S))


@asset('hub_rescue', (810, 1440), 48, 32, notes='R1b: 32 f, pencil + hubs 11.25 deg/f clockwise (frame 32 == '
       'hub_loop f0); the crinkled loop out of the centre head opening is drawn back in, 120 mm -> 0 by frame 31; '
       'shown 2-on (idx = (f - 512) // 2), comp upscales x1.333', mode='rescue', gpu_spp=256)
def build_hub_rescue(res, q):
    S = scene_hub(res, q, rescue=True)
    _spin_hubs(S['C'], -11.25, -2, 34)
    sc = bpy.context.scene
    st = dict(tape=None)

    def update(i):
        sc.frame_set(i)
        _remove(st['tape'])
        st['tape'] = rescue_tape(0.120 * (1.0 - i / 31.0), S['C']['root'], frame=i)
    return dict(update=update, features=lambda: hub_features(S))


@asset('label', (1080, 1920), 128, 1, labels=['still'], notes='R3: top-down side-A label (Mix \'98 / Side A, '
       'handwritten track list), pencil lying lower right', mode='static', mb=False, gpu_spp=512)
def build_label(res, q):
    S = scene_label(res, q)
    return dict(update=lambda i: None, features=lambda: label_features(S))


@asset('walkman_loop', (1080, 1920), 64, 8, notes='R4: keys up, LED on, spools in the lid window turn 7.5 deg/f '
       '(play direction, CCW seen from above); 8 f = 60 deg = one tooth period, frame 8 == frame 0. Comp reverses '
       '+ speeds it for REW', mode='loop', loop=True, gpu_spp=384)
def build_walkman_loop(res, q):
    S = scene_walk(res, q)
    _spin_hubs(S['W']['C'], 7.5, -2, 10)
    sc = bpy.context.scene
    return dict(update=lambda i: sc.frame_set(i), features=lambda: walk_features(S))


@asset('walkman_keys', (1080, 1920), 96, 4, labels=['play_down', 'rew_down', 'stop_down', 'led_off'],
       notes='CAM_WALK stills cropped to the key-row bbox + 24 px; paste at frame_xy over walkman_loop',
       mode='static', mb=False, gpu_spp=512)
def build_walkman_keys(res, q):
    S = scene_walk(res, q)
    Wk = S['W']
    states = {'play_down': ({'play'}, True), 'rew_down': ({'rew'}, True), 'stop_down': ({'stop'}, False),
              'led_off': (set(), False)}

    def update(i):
        down, led = states[ASSETS['walkman_keys']['labels'][i]]
        for nm, ko in Wk['keys'].items():
            ko.location.z = W_ZT - (0.0030 if nm in down else 0.0)
        Wk['led'].data.materials[0] = mat('led' if led else 'led_off')
    bpy.context.view_layer.update()
    pts = []
    for ko in Wk['keys'].values():
        for sx in (-1, 1):
            for sy in (-1, 1):
                for z in (-0.0035, W_KEY_UP + 0.0003):
                    pts.append(proj_px(wpos(ko, (sx * (W_KEY_W / 2 + 0.0004), sy * (W_KEY_D / 2 + 0.0004), z))))
    for sx in (-1, 1):
        for sy in (-1, 1):
            pts.append(proj_px(wpos(Wk['root'], (W_LED[0] + sx * 0.0015, W_LED[1] + sy * 0.0015, W_ZT + 0.001))))
    pts = np.asarray(pts)
    pad = CROP_PAD * res[0] / 1080.0
    border = [max(0, int(pts[:, 0].min() - pad)), max(0, int(pts[:, 1].min() - pad)),
              min(res[0], int(math.ceil(pts[:, 0].max() + pad))), min(res[1], int(math.ceil(pts[:, 1].max() + pad)))]
    return dict(update=update, features=lambda: walk_features(S), border=border)


@asset('walkman_eat', (810, 1440), 48, 32, notes='R4b: PLAY down, spools still; f0-f5 lid springs open 0 -> 26 -> 22 '
       'deg, f6-f31 the ribbon spills from the head opening over the front lip in crinkled curls onto the desk; '
       'frame 0 == walkman_loop frame 0 with PLAY down', mode='eat', gpu_spp=256)
def build_walkman_eat(res, q):
    S = scene_walk(res, q, keys_down=('play',))
    Wk = S['W']
    lr = Wk['lid_root']

    def lid(f):
        return LID_OPEN[f] if 0 <= f < len(LID_OPEN) else (0.0 if f < 0 else LID_OPEN[-1])
    _keyframe_rot(lr, lambda f: (0.0, -math.radians(lid(f)), 0.0), -1, 33)
    sc = bpy.context.scene
    st = dict(tape=None)

    def update(i):
        sc.frame_set(i)
        _remove(st['tape'])
        t = (i - 5) / 26.0
        frac = 0.0 if i < 6 else 1.0 - (1.0 - min(1.0, t)) ** 2.2
        st['tape'] = spill_tape(frac, i, Wk['root'])
    return dict(update=update, features=lambda: walk_features(S))


@asset('pencil_top', (600, 1700), 96, 2, labels=['key', 'shadow'], notes='R5: orthographic top-down pencil, eraser '
       'up, 1500 px long; key = pencil (RGBA), shadow = shadow-catcher pass (black, alpha = shadow)',
       mode='static', opaque=False, mb=False, gpu_spp=512)
def build_pencil_top(res, q):
    S = scene_pencil_top(res, q)
    objs = [o for o in bpy.data.objects if o.name.startswith('pencil') and o.type == 'MESH']

    def update(i):
        lab = ASSETS['pencil_top']['labels'][i]
        S['plane'].hide_render = lab == 'key'
        for o in objs:
            o.visible_camera = lab == 'key'
        for nm in ('rim', 'bounce'):                 # shadow pass = the key's contact shadow only (no soft veils)
            S['rig'][nm].hide_render = lab == 'shadow'

    def feats():
        f = dict(eraser_top=proj_px(wpos(S['P']['root'], (0, 0, P_LEN))), tip=proj_px(wpos(S['P']['root'], (0, 0, 0))),
                 ferrule=proj_px(wpos(S['P']['root'], (0, 0, P_FER_Z0 + P_FER / 2))))
        return {k: np.round(np.asarray(v, float), 1).tolist() for k, v in f.items()}
    return dict(update=update, features=feats)


# ============================================================================= render engine

def set_border(sc, rect, res):
    W, Hh = res
    x0, y0, x1, y1 = rect
    sc.render.use_border = True
    sc.render.use_crop_to_border = True
    sc.render.border_min_x = (x0 + 0.25) / W
    sc.render.border_max_x = (x1 + 0.25) / W
    sc.render.border_min_y = (Hh - y1 + 0.25) / Hh
    sc.render.border_max_y = (Hh - y0 + 0.25) / Hh


def render_asset(name, preview=False, samples=None, frames=None, scale=None):
    import cv2
    _bpy()
    A = ASSETS[name]
    W, Hh = A['size']
    k = scale if scale else (0.5 if preview else 1.0)
    res = (int(round(W * k / 2)) * 2, int(round(Hh * k / 2)) * 2)
    q = 0.5 if preview else 1.0
    t0 = time.time()
    build_textures()
    MATS.clear()
    global SPILL
    SPILL = None
    sc = reset(res, 16)
    spp = samples or (S_PREVIEW if preview else (A['gpu_spp'] if is_gpu() else A['spp']))
    sc.cycles.samples = spp
    S = A['build'](res, q)
    sc.render.film_transparent = not A['opaque']
    motion_blur(A['mb'] and A['n'] > 1, 0.5)
    border = S.get('border')
    if border:
        set_border(sc, border, res)
    outdir = os.path.join(PREVIEW if (preview or scale) else OUT, name, 'passes')
    os.makedirs(outdir, exist_ok=True)
    skip = os.environ.get('SKIP_EXISTING') == '1'
    if frames is None:
        mp = os.path.join(outdir, 'meta.json')
        if os.path.exists(mp):
            os.remove(mp)
        if not skip:
            for f in os.listdir(outdir):
                if f.endswith('.png'):
                    os.remove(os.path.join(outdir, f))
        idx = list(range(A['n']))
    else:
        idx = [i for i in frames if i < A['n']]
    if preview and frames is None:
        idx = sorted(set([0, A['n'] // 2, A['n'] - 1]))
    print(f'[{name}] scene {time.time() - t0:.1f}s; {res[0]}x{res[1]} border {border}; {spp} spp; frames {idx}; '
          f'device {DEVICE}' + ('' if is_gpu() else f' x{THREADS}'), flush=True)
    times = {}
    for i in idx:
        p = os.path.join(outdir, f'{i:04d}.png')
        if skip and os.path.exists(p):
            continue
        S['update'](i)
        t1 = time.time()
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        times[i] = round(time.time() - t1, 1)
        print(f'  {name} {i:02d}/{A["n"]} {A["labels"][i]}: {times[i]}s', flush=True)
    feats = S['features']()
    if border:
        def shift(v):
            if isinstance(v, dict):
                return {kk: shift(x) for kk, x in v.items()}
            a = np.asarray(v, float)
            if a.ndim == 1 and len(a) == 2:
                return [round(a[0] - border[0], 1), round(a[1] - border[1], 1)]
            if a.ndim == 1 and len(a) == 4:
                return [round(a[0] - border[0], 1), round(a[1] - border[1], 1), round(a[2] - border[0], 1),
                        round(a[3] - border[1], 1)]
            return [shift(x) for x in a.tolist()]
        feats = shift(feats)
        feats['frame_xy'] = [float(border[0]), float(border[1])]
    if frames is not None or (preview and A['n'] > 3):
        print(f'  -> {outdir} (partial: no meta.json) {time.time() - t0:.0f}s', flush=True)
        return None
    im0 = cv2.imread(os.path.join(outdir, '0000.png'), cv2.IMREAD_UNCHANGED)
    meta = dict(name=name, variant='passes', mode=A['mode'], frames=A['n'], fps_hint=30, size=[im0.shape[1], im0.shape[0]],
                loop=A['loop'], labels=list(A['labels']), notes=A['notes'], features=feats, samples=spp,
                preview=bool(preview), opaque=A['opaque'], motion_blur=bool(A['mb'] and A['n'] > 1),
                render_seconds=times, device=DEVICE, threads=None if is_gpu() else THREADS, scale=k,
                builder='pipeline/jawad_reels/assets3d_pencil_se_rewind.py')
    if border:
        meta['frame_xy'] = [int(border[0]), int(border[1])]
        meta['crop_rect_frame'] = list(map(int, border))
        meta['full_size'] = list(res)
    H.write_meta(outdir, **meta)
    print(f'  -> {outdir} {time.time() - t0:.0f}s total', flush=True)
    return meta


# ============================================================================= sheets, pack, restore

def _tile(p, h, bg):
    import cv2
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if im.shape[2] == 4:
        a = im[:, :, 3:4].astype(np.float32) / 255.0
        im = (im[:, :, :3].astype(np.float32) * a + np.array(bg, np.float32) * (1 - a)).astype(np.uint8)
    w = max(1, int(round(im.shape[1] * h / im.shape[0])))
    return cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)


def contact_sheet(root, tag, cell=480):
    import cv2
    rows = []
    for nm, A in ASSETS.items():
        d = os.path.join(root, nm, 'passes')
        if not os.path.isdir(d):
            continue
        fs = sorted(f for f in os.listdir(d) if f.endswith('.png') and f[:-4].isdigit())
        if not fs:
            continue
        pick = fs if len(fs) <= 4 else [fs[0], fs[len(fs) // 3], fs[2 * len(fs) // 3], fs[-1]]
        tiles = []
        for f in pick:
            for bg in ((20, 16, 14),) + (((200, 200, 200),) if not A['opaque'] else ()):
                t = _tile(os.path.join(d, f), cell, bg)
                cv2.putText(t, f'{nm} {f[:-4]}', (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1,
                            cv2.LINE_AA)
                tiles.append(np.pad(t, ((0, 0), (0, 6), (0, 0)), constant_values=255))
        rows.append(np.concatenate(tiles, 1))
    if not rows:
        return None
    wmax = max(r.shape[1] for r in rows)
    rows = [np.pad(r, ((0, 6), (0, wmax - r.shape[1]), (0, 0)), constant_values=255) for r in rows]
    os.makedirs(SHEETS, exist_ok=True)
    p = os.path.join(SHEETS, f'psr_{tag}_sheet.jpg')
    cv2.imwrite(p, np.concatenate(rows, 0), [cv2.IMWRITE_JPEG_QUALITY, 88])
    return p


def pack(quality=93):
    """Restore copies into brand_reels/assets/pencil_se_rewind/assets3d: opaque frames as JPEG q93 (alpha is 255),
    RGBA passes as PNG (max compression), meta.json as is. `restore` rebuilds the PNG spec folders."""
    import cv2
    import shutil
    if os.path.isdir(PACK):
        shutil.rmtree(PACK)
    total = 0
    for nm in ASSETS:
        src = os.path.join(OUT, nm, 'passes')
        if not os.path.exists(os.path.join(src, 'meta.json')):
            print('skip (no meta.json):', src)
            continue
        dst = os.path.join(PACK, nm, 'passes')
        os.makedirs(dst, exist_ok=True)
        for f in sorted(os.listdir(src)):
            sp = os.path.join(src, f)
            if f.endswith('.png'):
                im = cv2.imread(sp, cv2.IMREAD_UNCHANGED)
                if im.shape[2] == 4 and im[:, :, 3].min() == 255:
                    dp = os.path.join(dst, f[:-4] + '.jpg')
                    cv2.imwrite(dp, im[:, :, :3], [cv2.IMWRITE_JPEG_QUALITY, quality])
                else:
                    dp = os.path.join(dst, f)
                    cv2.imwrite(dp, im, [cv2.IMWRITE_PNG_COMPRESSION, 9])
            else:
                dp = os.path.join(dst, f)
                shutil.copy2(sp, dp)
            total += os.path.getsize(dp)
    print(f'pack {PACK}: {total / 1e6:.1f} MB (JPEG q{quality})')
    if total > 58e6 and quality > 70:              # BUILD_CONTRACT: the restore folder stays under 60 MB
        return pack(quality - 8)
    return total


def restore():
    """Rebuild RWS/assets3d/<name>/passes (RGBA 8-bit PNG + meta.json, meta written last) from the pack."""
    import cv2
    import shutil
    for nm in sorted(os.listdir(PACK)):
        src = os.path.join(PACK, nm, 'passes')
        dst = os.path.join(OUT, nm, 'passes')
        os.makedirs(dst, exist_ok=True)
        for f in sorted(os.listdir(src)):
            if f.endswith('.jpg'):
                im = cv2.imread(os.path.join(src, f), cv2.IMREAD_COLOR)
                im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
                cv2.imwrite(os.path.join(dst, f[:-4] + '.png'), im)
            elif f.endswith('.png'):
                shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
        if os.path.exists(os.path.join(src, 'meta.json')):
            shutil.copy2(os.path.join(src, 'meta.json'), os.path.join(dst, 'meta.json'))
        print('restored', dst)


def selftest():
    import cv2
    ok = True
    for nm, A in ASSETS.items():
        d = os.path.join(OUT, nm, 'passes')
        mp = os.path.join(d, 'meta.json')
        if not os.path.exists(mp):
            print(f'{nm}: MISSING meta.json')
            ok = False
            continue
        meta = json.load(open(mp))
        fs = sorted(f for f in os.listdir(d) if f.endswith('.png') and f[:-4].isdigit())
        im = cv2.imread(os.path.join(d, fs[0]), cv2.IMREAD_UNCHANGED)
        good = len(fs) == meta['frames'] == A['n'] and im.dtype == np.uint8 and im.shape[2] == 4
        ok &= good
        print(f'{nm}: {len(fs)} frames, {im.shape[1]}x{im.shape[0]} {im.dtype} ch{im.shape[2]} -> {"ok" if good else "FAIL"}')
    print('selftest', 'ok' if ok else 'FAIL')
    return ok


def main(argv):
    if not argv:
        print(__doc__)
        return
    preview = '--preview' in argv
    samples = int(argv[argv.index('--samples') + 1]) if '--samples' in argv else None
    scale = float(argv[argv.index('--scale') + 1]) if '--scale' in argv else None
    frames = [int(x) for x in argv[argv.index('--frames') + 1].split(',')] if '--frames' in argv else None
    skipv = set()
    for flag in ('--samples', '--scale', '--frames'):
        if flag in argv:
            skipv.add(argv.index(flag) + 1)
    names = [a for i, a in enumerate(argv) if not a.startswith('--') and i not in skipv]
    if names == ['textures']:
        build_textures(force=True)
        return
    if names == ['savetex']:
        save_textures()
        return
    if names and names[0] == 'cams':
        cams_report(names[1:] or None)
        return
    if names in (['sheet'], ['previewsheet']):
        print(contact_sheet(PREVIEW if names == ['previewsheet'] else OUT,
                            'preview' if names == ['previewsheet'] else 'finals'))
        return
    if names == ['pack']:
        pack()
        return
    if names == ['restore']:
        restore()
        return
    if names == ['selftest']:
        selftest()
        return
    if names == ['all']:
        names = list(ASSETS)
    for nm in names:
        if nm not in ASSETS:
            raise SystemExit(f'unknown asset {nm!r}; have {list(ASSETS)}')
    for nm in names:
        render_asset(nm, preview=preview, samples=samples, frames=frames, scale=scale)


if __name__ == '__main__':
    main(sys.argv[1:])
