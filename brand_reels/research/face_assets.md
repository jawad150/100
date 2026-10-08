# Jawad face / body asset library (character sheets -> 2.5D-ready cut-outs)

Built 2026-10-08, fully local (no Higgsfield, no paid generation). Source: Jawad's two character sheets
(`workspace/brand_reels/charsheet/sheet_streetwear.webp`, `sheet_suit.webp`). Everything heavy lives in the
git-ignored workspace; this page is the map.

| what | where (`CS = /home/user/100/workspace/brand_reels/charsheet`) |
|---|---|
| 14 native crops, labels excluded | `CS/crops/<name>.png` |
| 14 Real-ESRGAN 2x masters | `CS/crops/<name>_2x.png` |
| **14 RGBA cut-outs (2x, straight alpha, sRGB, decontaminated)** | `CS/cutouts/<name>.png` |
| 14 depth maps (16-bit, white = near, edge-extended) | `CS/cutouts/<name>_depth.png` |
| 14 metadata files (crop box, eyes, nose, mouth, face / head box, open sides, QA numbers) | `CS/cutouts/<name>.json` |
| helper module (load, depth, meta, rim light, halo, duotone, halftone, cine grade, parallax, idle, swaps) | `CS/tools/faces.py` |
| pipeline scripts (SR, matte, depth, meta, tests, contact sheet) | `CS/tools/{sr,matte,depth,meta,grade_tests,contact,test_snippets}.py` |
| contact sheet (all cut-outs on a checker + depth inset) | `CS/contact_sheet.jpg` |
| edge checks (black / #FF4A1C / white + 3x hair zoom) | `CS/tests/edges_<name>.jpg` |
| brand-grade boards (4 looks, 1080x1920) | `CS/tests/board_<name>.jpg`, `CS/tests/look_<name>_<A..D>.jpg` |
| proof stills of every snippet below | `CS/tests/snip_*.jpg`, strip `CS/tests/snip_strip.jpg` |

## 1. Pipeline and what each step fixed

| step | tool (local) | notes |
|---|---|---|
| crop | PIL, panel borders measured from the sheets (white gutters on the suit sheet, figure components on the streetwear sheet) | printed labels excluded; native px kept (no resampling) |
| 2x super-resolution | Real-ESRGAN **x4plus** ONNX (`imgdesignart/realesrgan-x4-onnx`, weights BSD-3, xinntao), 64 px tiles, x4 then area-down to 2x | 80-120 s per headshot, 220-300 s per full body (2 threads). `realesr-general-x4v3` (`tools/sr.py general`, 7 s) is also installed: softer, more plastic skin; x4plus kept the eyes / brows / beard better. Lanczos 2x was clearly softer and kept the source's webp blocking |
| background removal | **BiRefNet-portrait** ONNX (rembg release `BiRefNet-portrait-epoch_150.onnx`, md5 c3a64a6a..., MIT) at 1024^2 via onnxruntime | ~45 s each, **peak RAM ~9 GB** (two runs were OOM-killed while another agent's TTS server held 4 GB: run it alone). rembg 2.0.85 installed in `CS/.venv`, only its model file is used |
| edge solve | studio backdrop modelled as a smooth plate B; in the soft band alpha re-solved in LINEAR light along the backdrop -> subject colour line (only where subject / backdrop contrast is high, so the white tee on the light-grey sweep is left to the net) | removes the grey fringe on hair and beard; a guard keeps the network's confident interior (grey hair sheen cannot become see-through specks) |
| clean-up | keep subject component(s); fill only enclosed specks < 0.004 % of the image; real see-through gaps (between the knees in the power pose) stay open; alpha < 3 % -> 0 | |
| colour decontamination | `pymatting.estimate_foreground_ml` in linear light | halo over black: **-0.5 to -1.9 code values** (pass is <= +6) vs **+5.7 to +10.8** for the raw photo colours with the same matte |
| cut borders | panel crops carry 1 px of sheet background at the cut; the outer 3 px on every border the subject touches are replicated from inside | no light line along bust bottoms |
| depth | **Depth-Anything-V2-Small** ONNX (`onnx-community/depth-anything-v2-small`, Apache-2.0; Base/Large are non-commercial and were not used), short side 630 px, run on the photo with its backdrop | normalised inside the matte (1st / 99.5th pct), seeds taken 1 % inside the silhouette (skips the net's soft fall-off), smooth normalised-convolution fill outward so edges travel with the subject |
| landmarks | YuNet face detector (OpenCV zoo, MIT) on the 2x masters | eyes, nose, mouth corners, face box -> `head_box` for the rigid head plane, `eye_mid` for eye-locked swaps |

Rebuild one asset (from `CS`, one heavy job at a time):

```bash
. .venv/bin/activate; export OMP_NUM_THREADS=2
nice -n 10 python3 -I tools/sr.py x4plus crops/X.png crops/X_2x.png --threads 2
nice -n 10 python3 -I tools/matte.py crops/X_2x.png cutouts/X.png --raw tests/raw_X.png --threads 2   # add --reuse to skip the net
nice -n 10 python3 -I tools/depth.py crops/X_2x.png cutouts/X.png cutouts/X_depth.png --threads 2
python3 -I tools/meta.py X && python3 tools/contact.py && python3 tools/grade_tests.py edges X
```

## 2. Inventory

Sizes: native crop -> 2x cut-out (px). "Face" = YuNet face-box height in the NATIVE crop (the face-compositor
rule: faces under ~250 px native are mid-shot material, never a full-frame close-up). Max display = subject bbox
at scale 1.0 of the 2x master (do not scale above 1.0). Open = borders the panel crop cuts the subject on
(b bottom, l left, r right): anchor busts on the frame bottom and `FA.fade_open` the sides. Gaze is screen
direction: put the UI card / keyword / other character where he looks.

| file | outfit, pose, gaze | expression -> emotion | best story use (Jawad = video editor) | px native -> 2x | face | max display | open | quality notes |
|---|---|---|---|---|---|---|---|---|
| `street_fullbody_powerpose` | streetwear, full body, leaning back, both hands on the bomber's lapels, chin up, to camera | cocky half-smile -> swagger, "main hoon na" | title / end card hero, "creator mode on", walk-in reveal, the "after" in a glow-up | 480x1014 -> 960x2028 | 103 | 809x1954 | - | clean; the knee gap is correctly see-through; hands, chains, sneakers sharp. Mid/wide shots only (small face) |
| `street_threequarter_turn` | streetwear, full body, 3/4 profile facing **screen-left**, arms down, watch | neutral, focused -> observing | standing in front of a giant timeline / client brief on the left, entering the edit suite, "pehle samjho, phir edit" | 410x1024 -> 820x2048 | 117 | 505x1971 | - | clean; narrow silhouette suits a split screen with UI on the left |
| `street_smirk` | streetwear bust, head tilted, chin down, eyes to camera | cocky smirk -> playful confidence | the punchline after the problem ("aur phir maine edit kiya..."), challenge accepted, reply to a doubter comment | 457x473 -> 914x946 | 208 | 888x899 | b | best streetwear close-up source; texture crisper than source (SR native ratio 2.2) |
| `street_sunglasses` | streetwear bust, sunglasses, face turned **screen-left** | cool, unreadable -> flex | deal closed, "rate double", the cool exit, cover / thumbnail | 450x473 -> 900x946 | 201 | 893x902 | b r | lenses dark grey with a soft reflection (keep, do not recolour); jacket cut at the right edge -> fade_open |
| `street_chinup_gaze` | streetwear bust, chin up, looking up **screen-left** | hopeful, determined -> ambition | "sapna", looking up at a floating keyword / view counter / 3D logo, the turning point of a journey story | 470x482 -> 940x964 | 212 | 890x917 | b | one 9 px see-through speck in the hair crest was filled; eye-line is up-left: put the target there |
| `suit_fullbody` | 3-piece black suit, full body, frontal, arms down | neutral, composed -> authority | "agency-level" moment, standing on a stage / podium, end card, the pro half of a "freelancer vs brand" split | 469x1125 -> 938x2250 | 123 | 763x2113 | - | clean; floor and shadow removed (add `FA.contact_shadow`); glossy shoes keep their highlights |
| `suit_neutral` | suit bust, frontal, to camera | calm, serious -> straight talk | the narrator face for a statement ("seedhi baat"), intro line, the calm before the hook | 406x556 -> 812x1112 | 220 | 812x1049 | b l r | frizzy fringe on the left of the hair shows a few see-through specks over bright colour (invisible on dark worlds); pocket square bottom-right is his |
| `suit_threequarter` | suit bust, head turned **screen-right**, eyes right | narrowed eyes, pursed lips -> skeptical side-eye | reading a client message / notification placed screen-right ("500 mein ho jayega?"), doubt beat | 382x556 -> 764x1112 | 246 | 764x1043 | b l r | largest suit face; strong eye-line for a UI card on the right |
| `suit_profile` | suit, full profile facing **screen-right** | lips pressed -> concentration, resolve | rim-light silhouette hero, "raat ke 3 baje" grind, looking at a glowing timeline / the next scene, transitions (whip past the nose) | 355x556 -> 710x1112 | 202 | 642x1046 | b l | best silhouette for the brand rim (nose, beard, quiff); front of the face is clear of the border |
| `suit_smirk` | suit bust, head turned **screen-left**, eyes back to camera | half smile -> smug, knowing | "maine pehle hi bola tha", the setup line right before the payoff, answering a hater | 355x556 -> 710x1112 | 231 | 710x1047 | b l r | clean |
| `suit_shocked` | suit bust, frontal | wide eyes, raised brows, mouth shut -> shock, disbelief | the HOOK reaction: "client: bas thoda sa change" at 2 AM, "final_final_v7", seeing the budget / the render time | 406x561 -> 812x1122 | 221 | 812x1077 | b l r | clean; pairs with confused / smiling for eye-locked swaps (all frontal, same scale) |
| `suit_confused` | suit bust, frontal, head slightly tilted | knitted brows, mouth open mid-word -> confusion, "kya?" | the problem statement: "logo bada karo", "isko viral bana do", "exposure milega" | 382x561 -> 764x1122 | 228 | 764x1079 | b l r | one of only two open-mouth frames; not lip-sync material |
| `suit_smiling` | suit bust, frontal | closed-mouth genuine smile -> relief, happiness | the payoff: "payment received", "client: perfect!", warm CTA ("follow karo") | 355x561 -> 710x1122 | 213 | 710x1077 | b l r | clean |
| `suit_hand_on_chest` | suit bust, head turned slightly **screen-right**, eyes up-right, right hand on chest, watch | sincere, mouth open -> gratitude / "trust me" (or mock "mujhe?") | sincerity beat, thanking the audience, "dil se banaya", humble-brag | 355x561 -> 710x1122 | 195 | 710x1085 | b l r | fingers and watch clean; the hand is a natural foreground layer (split it for an L3 plane if needed) |

Pairings that cut well (same framing and scale, eyes locked with `eye_mid`): `suit_shocked -> suit_confused ->
suit_smiling` (problem -> payoff arc), `suit_neutral <-> suit_smirk`, `street_chinup_gaze -> street_smirk`
(dream -> confidence), `suit_profile -> suit_neutral` (turn to camera, hidden by a whip).

## 3. Brand-grade tests (on the `ember` world, 1080x1920)

Boards: `CS/tests/board_{street_smirk,suit_shocked,suit_profile,street_fullbody_powerpose,street_sunglasses}.jpg`.

| look | function | verdict |
|---|---|---|
| A rim | `FA.rim_light(plain, dep, light=(0.8, -0.5))`: low-key warm subject (exposure 0.42), FLAME back-rim on the light side + RED counter-rim + thin all-round outline (screen-space from the alpha gradient), depth-normal wrap restricted to the silhouette zone, emissive halo; no rim / halo along cut borders | **KEEP (hero look).** Reads exactly like his "younger self" cover: natural skin, glowing flame outline, black clothes stay black |
| B duotone | `FA.duotone(plain, glow=0.35)`: perceptual luma -> black / #3A0603 / #B3150A / FLAME / #FFA060 / peach | **KEEP for punchy beats** (hook flash, "ERROR" moments, beat-synced cut-ins). Too stylised to hold > 1 s |
| C halftone | `FA.halftone(plain, cell=9)`: flame dots sized by brightness on near-black | **Transitions only** (print / comic beat, 2-6 frames). Shirts and skin flatten to one yellow-orange; not premium for holds |
| D cine | `FA.rim_light(..., base=FA.cine_grade(plain), gain=1.4, halo_strength=0.35)`: S-curve with a toe (blacks crushed, never lifted), warm split tone, 0.82 sat + softer rim from the left | **KEEP (dialogue / narration look).** Most natural face; use when he "talks" for several beats |

Default for the set: A for hero / end-card shots, D for narration, B as a beat accent, C as a transition texture.
Every look is built once per worker (`functools.lru_cache`), ~1 s each; drawing a look costs one `K.draw`.

## 4. Limitations (read before boarding a shot)

- **No lip-sync, no talking head.** Twelve stills are closed-mouth, two are open (`suit_confused`,
  `suit_hand_on_chest`). The voice-over is narration over visuals; never alternate open / closed mouths to fake
  speech, never warp a mouth, no fake blinks, no eye re-targeting, no morphs between poses.
- **Static photos -> 2.5D only:** (1) the cut-out as a plane in `K.Scene` against the world (camera yaw <= 4 deg,
  pitch <= 3, roll <= 2, push <= 8 %/s); (2) head and torso as separate rigid layers (`FA.split_head`), head
  leading by <= 4 px; (3) depth micro-parallax with `FA.parallax(..., rigid_box=head_box)` so the face never
  warps; (4) puppet idle (`FA.idle`: <= 0.4 % breathing at ~0.3 Hz, 0.5 deg sway, 3 px drift); (5) expression
  swaps on a beat: HARD CUT, eyes locked via `meta['eye_mid']`, 1.00 -> 1.03 push-in on the new pose
  (`FA.swap_push`), or hidden by a whip / occluder. Never cross-dissolve two faces. Max ~3.5 s on one still pose.
- **Resolution.** The sources are small (faces 195-246 px native in headshots, 103-123 px in full bodies). Keep
  display scale <= 1.0 of the 2x master: a bust is 710-940 px wide on a 1080 frame, i.e. a medium shot with world
  around it, not a full-bleed close-up. `street_smirk` at 1.18 still held up under the rim look + grain
  in an earlier look test (the boards now use the 1.0 cap); beyond that it goes soft. Full bodies fill ~1700 px of height at 0.8-0.85.
- **Super-resolution character.** x4plus sharpens eyes, brows, beard and chains and smooths skin slightly
  (cheek texture vs the source at native scale: 0.8-1.5x on the suit sheet, ~2.0-2.3x on the streetwear headshots,
  i.e. crisper than the source). The finish's grain sits on top; if a street close-up reads crunchy next to suit
  shots, blend: `lanczos2x + 0.55 * (sr - lanczos2x)` (checked on `suit_shocked` / `street_sunglasses`: keeps most of the
  eye and beard detail, softer edges).
- **Panel cuts.** Busts are cut flat at the bottom and often at the shoulders: anchor the bottom at or below
  `K.H` (bust bottom = `eye_y_screen + (h - eye_mid_y) * scale` must be >= 1920) and use `FA.fade_open` on the
  sides. A bust can never fly in from below with its bottom visible.
- **Two wardrobes, two hair styles.** Streetwear = high skin fade with a hard part; suit = fuller side-swept
  hair, no fade. Treat them as two "modes" (creator / pro, before / after), never as one continuous moment.
  Mirroring (`spr[:, ::-1]`) fixes an eye-line but flips the parting, watch and pocket square: never place a
  mirrored shot next to an unmirrored one of the same outfit.
- **Baked lighting.** Soft frontal studio light is in the photos; the brand rim is added in 2D. Keep the subject
  darker than the world's key (`warm_dark` exposure 0.4-0.6) so the flat front light does not fight the rim, and
  put the rim on the side of the scene's main glow (`light=` is a screen direction, y down).
- **Depth maps are relative and soft** (monocular, 630 px short side): good for normals, rim wrap, layer
  splitting and +-4 px parallax, not for camera orbits, re-posing or relighting from the front.
- **Hair fringe.** The suit sheet's frizzy fringe keeps a few see-through specks that show on bright or saturated
  backgrounds (invisible on the dark worlds). Over a flat bright colour, add `FA.halo` or a 1 px alpha dilate.
- **AI imagery.** The character sheets look AI-generated. Using them (and an AI voice) may need Meta's AI label:
  open question for the lead, not decided here.

## 5. Python: load and composite with the Reels Studio toolkit

Conventions: every sprite is a premultiplied LINEAR-light float32 (h, w, 4) array (`K.load_image` converts the
straight-alpha sRGB PNG); colours via `K.hexlin`; looks are built once and are read-only; `light=` and `rot` use
canvas screen directions (y down). The project toolkit copy is `pipeline/jawad_reels` (its `project.json` maps the
palette to FLAME / RED / EMBER / AMBER); `import jawad_kit` first. Every block below was executed in order by
`CS/tools/test_snippets.py` against the real assets (stills in `CS/tests/snip_*.jpg`; measured on the shared box:
bust frame with `ember` background and post ~0.2 s, 3D scene ~0.2 s, depth micro-parallax ~0.2 s).

### 0. Setup (top of any reel module that shows Jawad)

```python
import sys, functools
sys.path[:0] = ['/home/user/100/pipeline/jawad_reels',                    # project toolkit copy + project.json palette
                '/home/user/100/workspace/brand_reels/charsheet/tools']   # faces.py (this library)
import jawad_kit                       # FIRST: brand palette, looks 'ember' / 'noir_ember', house type styles
from jawad_kit import K, T, J
import numpy as np, cv2
import faces as FA

spr = FA.load('suit_shocked')          # = K.load_image(cutouts/suit_shocked.png): premultiplied LINEAR float32 (h, w, 4)
dep = FA.depth('suit_shocked')         # float32 (h, w) 0..1, 1 = nearest, edge-extended past the matte
m = FA.meta('suit_shocked')            # eyes / eye_mid / face_box / head_box / open_sides / max_display_w ...
```

Same thing with the bare toolkit (no faces.py):

```python
CUT = '/home/user/100/workspace/brand_reels/charsheet/cutouts/'
spr = K.load_image(CUT + 'suit_shocked.png')               # straight-alpha sRGB PNG -> premultiplied linear, cached
small = K.load_image(CUT + 'suit_shocked.png', size=600)    # width 600 px, aspect kept, area-filtered
dep = cv2.imread(CUT + 'suit_shocked_depth.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535.0
```

### 1. Build looks once, draw a bust on the frame bottom (2D, idle breathing)

```python
POSES = ('suit_neutral', 'suit_shocked', 'suit_confused', 'suit_smiling')

@functools.lru_cache(maxsize=1)
def faces():                                    # ~1 s per look: build once per render worker
    out = {}
    for n in POSES:
        plain = FA.load(n)
        hero = FA.rim_light(plain, FA.depth(n), light=(0.8, -0.5))          # rim from top-right
        out[n] = (plain, FA.fade_open(hero))     # fade the panel-cut shoulders into the dark (not the bottom)
    return out

def draw(t):
    cv = K.background('ember', t)                          # frame total ~0.2 s with post (measured)
    plain, hero = faces()['suit_neutral']
    dx, dy, rot, (sx, sy) = FA.idle(t, seed=2)              # <= 0.4 % breathing, 0.5 deg sway, 3 px drift
    s = 1.0                                                 # display scale <= 1.0 of the 2x master
    bottom_mid = (plain.shape[1] / 2, plain.shape[0])       # cut-out px -> anchor inside the padded look
    K.draw(cv, hero, K.CX + dx, K.H + 6 + dy, scale=(s * sx, s * sy), rot=rot,
           anchor=FA.anchor_at(plain, hero, bottom_mid))
    return K.post(cv, 'ember', t)
```

### 2. Expression swap on a beat (hard cut, eyes locked, 1.00 -> 1.03 push-in)

```python
BPM = 100
T_SWAP = K.beat(8, BPM)                 # the swap lands on beat 8
EYES = (540.0, 1165.0)                  # screen point of the eye midpoint (bust bottom stays below K.H)

def draw_face(cv, t):
    name = 'suit_shocked' if t < T_SWAP else 'suit_confused'
    plain, hero = faces()[name]
    s = 0.98 * FA.swap_push(t, T_SWAP)  # the NEW pose pushes in; never cross-dissolve two faces
    K.draw(cv, hero, EYES[0], EYES[1], scale=s, anchor=FA.anchor_at(plain, hero, FA.meta(name)['eye_mid']))
    # check: the bust must cover the frame bottom -> EYES[1] + (plain.shape[0] - eye_mid_y) * s >= K.H
```

### 3. Real 2.5D: the cut-out as a plane in a K.Scene (camera parallax against the world + DOF)

```python
def draw_3d(t):
    u = K.EASE['easy_ease'](K.clamp(t / 3.0))
    cam = K.Cam.orbit((0, 0, 0), 1500, yaw=K.lerp(-3.0, 3.0, u), pitch=K.lerp(1.0, -1.0, u), aperture=24)
    cv = K.background('ember', t, cam)                      # far plate (pans like a distant backdrop)
    sc = K.Scene(cam)
    plain, hero = faces()['suit_neutral']
    ax, ay = FA.anchor_at(plain, hero, (plain.shape[1] / 2, plain.shape[0]))
    sc.plane(hero, (0, 975, 0), hero.shape[1], anchor=(ax, ay))      # z=0: 1 world unit = 1 px, scale 1.0
    sc.particles(J.embers(120, seed=4), t)                  # warm sparks in front of / behind him, with DOF
    return K.post(sc.render(cv), 'ember', t)
```

### 4. Head as one rigid plane over the torso (inner parallax without warping the face)

```python
plain = FA.load('suit_neutral')
hero = FA.fade_open(FA.rim_light(plain, FA.depth('suit_neutral')))
head, torso = FA.split_head(hero, FA.meta('suit_neutral'), off=FA.offset(plain, hero))
anchor = FA.anchor_at(plain, hero, (plain.shape[1] / 2, plain.shape[0]))

def draw_split(cv, t):
    u = K.EASE['easy_ease'](K.clamp(t / 3.0))
    lead = K.lerp(-3.0, 3.0, u)                             # head leads the torso by <= 4 px per shot
    K.draw(cv, torso, K.CX + 0.4 * lead, K.H + 6, anchor=anchor)
    K.draw(cv, head, K.CX + 1.4 * lead, K.H + 6 - 0.3 * abs(lead), anchor=anchor)
```

### 5. Depth micro-parallax (torso / hair edges only, the face stays rigid)

```python
name = 'street_smirk'
plain = FA.load(name)
hero = FA.fade_open(FA.rim_light(plain, FA.depth(name)))
dep_h = FA.depth_like(name, plain, hero)                    # depth padded exactly like the look
dx0, dy0 = FA.offset(plain, hero)
hb = [v + o for v, o in zip(FA.meta(name)['head_box'], (dx0, dy0, dx0, dy0))]

def draw_micro(cv, t):
    k = K.lerp(-1.0, 1.0, K.EASE['easy_ease'](K.clamp(t / 3.0)))
    moved = FA.parallax(hero, dep_h, dx=4.0 * k, dy=0.0, rigid_box=hb)   # ~0.1-0.2 s per frame (remaps)
    K.draw(cv, moved, K.CX, K.H + 6, anchor=FA.anchor_at(plain, hero, (plain.shape[1] / 2, plain.shape[0])))
```

### 6. House device: serif keyword BEHIND the head

```python
key = T.render('sapna', 'jw_key', px=300)                    # cached sprite; T.measure() for widths

def draw_keyword_behind(cv, t, name='suit_smiling'):
    plain, hero = faces()[name]
    hair_top = K.H + 6 - (plain.shape[0] - FA.meta(name)['subject_bbox'][1])   # screen y of the hair crest
    key.draw(cv, 540, hair_top - 35)                         # keyword first: only its lower third meets the hair ...
    K.draw(cv, hero, K.CX, K.H + 6,                          # ... then Jawad over it (>= 70 % of the word readable)
           anchor=FA.anchor_at(plain, hero, (plain.shape[1] / 2, plain.shape[0])))
```

### 7. Full body on a floor (feet anchor + contact shadow)

```python
@functools.lru_cache(maxsize=1)
def full():
    p = FA.load('street_fullbody_powerpose')
    return p, FA.rim_light(p, FA.depth('street_fullbody_powerpose'), light=(-0.8, -0.4))

def draw_full(cv, t, feet=(540.0, 1760.0), s=0.80):
    plain, hero = full()
    x0, y0, x1, y1 = K.alpha_bbox(plain, 0.5)
    K.draw(cv, FA.contact_shadow((x1 - x0) * s * 0.9), feet[0], feet[1], mode='over')
    K.draw(cv, hero, feet[0], feet[1], scale=s, anchor=FA.feet_anchor(hero))
```

### 8. Stylised flash frames (cut, do not dissolve)

```python
@functools.lru_cache(maxsize=None)
def stylised(name, kind):
    p = FA.load(name)
    look = {'duotone': lambda: FA.duotone(p, glow=0.35),     # black -> ember -> red -> flame -> peach
            'halftone': lambda: FA.halftone(p, cell=9.0),    # flame dots on near-black (comic / print beat)
            'cine': lambda: FA.rim_light(p, FA.depth(name), light=(-0.8, -0.45), gain=1.4, halo_strength=0.35,
                                         base=FA.cine_grade(p))}[kind]()
    return FA.fade_open(look)
```

### 9. faces.py API (one line each)

| call | does |
|---|---|
| `FA.load(name, size=None, scale=None)` | cut-out sprite (cached, read-only) |
| `FA.depth(name, shape=None)` / `FA.depth_like(name, plain, hero)` | depth 0..1 (1 = near) / padded like a look |
| `FA.meta(name)` | dict from `cutouts/<name>.json` (`eyes`, `eye_mid`, `nose`, `mouth`, `face_box`, `head_box`, `subject_bbox`, `open_sides`, `max_display_w/h`, `halo_cv`, `tex_ratio_native`, `sheet_box`) |
| `FA.rim_light(spr, dep, light=(x, y), gain=2.4, back=0.5, outline=0.15, depth_wrap=0.3, halo_strength=0.55, base=None)` | brand rim look (padded on closed sides only) |
| `FA.halo(spr, color, sigmas, strength)` | emissive glow around the silhouette, none on cut borders |
| `FA.warm_dark(spr)`, `FA.cine_grade(spr)`, `FA.duotone(spr, glow=)`, `FA.halftone(spr, cell=)` | base grades / stylised looks |
| `FA.fade_open(spr, sides=('left', 'right'))` | fade the panel-cut borders (after the look) |
| `FA.offset(plain, hero)`, `FA.anchor_at(plain, hero, point)`, `FA.feet_anchor(spr)` | place looks by cut-out pixels (eyes, bust bottom, feet) |
| `FA.split_head(hero, meta, off=)` | rigid head layer + torso layer |
| `FA.parallax(spr, dep, dx, dy, zoom, rigid_box=)`, `FA.rigid_depth(dep, box)` | depth micro-parallax with a rigid face |
| `FA.idle(t, seed)`, `FA.swap_push(t, t_swap)`, `FA.eye_align(meta_a, meta_b, scale_a, scale_b, xy_a)` | puppet idle, swap push-in, eye alignment |
| `FA.contact_shadow(width)`, `FA.bottom_fade(spr, frac)`, `FA.open_sides(spr)` | floor contact, bust bottom fade, cut-border test |
