# Transitions, Sound and Music Bible: @jawad_mp4 cinematic storytelling reels

**For:** Jawad (@jawad_mp4), video editor and motion designer. His page is his own personal brand, for a Pakistani + Indian audience.
**Scope:** 5 reels, 30-40 s each, 1080x1920 at 30 fps. Hinglish / Roman Urdu voice-over (VO) by a Hindi-speaking male TTS voice, with Roman Urdu captions.
**Brand:** FLAME orange and RED on deep warm black.
**Engine:** the Reels Studio toolkit plus `pipeline/jawad_reels/jawad_kit.py` (looks `ember` and `noir_ember`, house type, `J.underline`, `J.embers`). Everything is made locally.
**Date:** 2026-10-08. Owner of this file: the transitions/sound/music research pass.
**Status:** research and design spec. No code has been written yet. Every API named below exists in `toolkit/core.py`, `type3d.py`, `ui.py`, `audio.py` or `jawad_kit.py`, unless it is marked **[ADD]**. An [ADD] item is new code for `jawad_tx.py` (transitions), `jawad_sfx.py` (shared custom SFX) or `score.py` (music). Section 2.5 and Section 5.4 give the proposed owners and designs.

> 1M views is a *stretch goal*, never a promise. This bible covers craft levers only. Retention, hooks and share triggers live in `hooks_retention_captions.md` and `niche_competitors.md`. The reference teardowns are `ref1_analysis.md` and `ref2_analysis.md`. This file is consistent with all of them and cites them.

---------------------------------------------------------------------------------------------------------------

## 0. One-page cheat card (print this)

| decision | rule |
|---|---|
| Frame grid | 30 fps. A cut is quantised to a frame. A hard cut switches scenes **half a frame early**: `t + HALF >= c` with `HALF = 0.5/30`. Then motion blur never crosses a cut (§2.4). |
| Tempo | Use a **frame-locked BPM** (Section 2.1): **75** (emotional), **90** (storytelling), **100** (cinematic drive), **112.5** (craft/montage), **150** (hype; the same grid as 75). Set DUR to a whole number of bars. |
| Where cuts go | Section changes on bar lines (beat 1). Hard cuts on beats. Montage flicks on 8ths. **A transition's cut point sits on the grid, not its start.** |
| VO vs cuts | Hero transitions go in **VO gaps**. Ref2 puts transitions 0.03-0.65 s after a phrase ends. The next line **pre-laps the cut by 4-9 frames** (ref2 measured 0.29 s). |
| Flash | **Never** `K.flash` / `K.fade` / `post(flash=)` (they lift the blacks). Use an exposure push: `exposure=1.4*push`, bloom ×(1+0.9·push), push = `K.impulse(t, c-0.02, decay=16)`. |
| Motion blur | 3 samples by default. 5 for moves of 300-1500 px/s. **7** for whips, zoom-throughs and fly-throughs. 9 only for a shatter that crosses the lens. Top up with `K.whip_blur(cv, ≈0.5·px_per_frame)` (capped at 900). |
| Transition budget per reel | 10-16 shots in 30-40 s, at most **4 feature transitions** (at most 2 of them ★), never two features within 2 bars. The rest are beat cuts with an exposure push or a J-cut. |
| Families | **One transition family per reel. No two reels share a family or a signature device** (playbook rule). Section 3.0 gives the allocation. |
| Loudness | Final **-14 LUFS** integrated (±0.5), TP **≤ -2.0 dBTP** in the wav and ≤ -1.5 after AAC, LRA 5-9 LU. VO stem **-16 LUFS**. SFX stem -18 LUFS (audio.py default). Music under VO is **≥ 8 LU below speech** (median). |
| Ducking | Detail SFX inside VO lines **-4 to -8 dB**. Music under VO: broadband -6 dB plus a 2.5 kHz dynamic dip -4 dB (≈ -10 dB in the speech band). Hero hits are never on top of words. |
| Carve | Under the VO, SFX are either **dark** (`'lp': 900-1200`) or **air** (`'hp': 5000-6000`). Nothing busy in **1-4 kHz** while a word is spoken. |
| Silence | One **drop-out per reel**, at the reveal: ½-1 beat (10-24 frames). True silence is at most about 8 frames; otherwise a breath, a heartbeat or a −45 LUFS room tone remains. Then the loudest hit of the reel lands. |
| Risers | End **on** the hit (`align='hit'`), or end where the drop-out starts. Length: 1 beat (small), 2 beats (section), 4 beats (hero). |
| Hit stack | transient + body + sub + tail, with layers offset 0-5 ms (§4.2). At most 3 sounds on one instant. `A.duck_under` handles clusters. |
| Desi | **One desi voice per reel** (tabla OR sitar OR harmonium OR dholak) plus at most a tanpura drone. Tune to Sa. Use it as punctuation, not wallpaper (§4.7). |
| Music | An original score from `score.py` (§5.4) is the default. Name it "Original audio · <hook phrase> · @jawad_mp4". The trending-audio path uses a VO+SFX stem plus an in-app track at 10-20 % (§5.6). |
| Loop | The last bar resolves *into* frame 0, with the same drone or chord. **Never fade to black or to silence** (`hooks_retention_captions.md` §loop). |

---------------------------------------------------------------------------------------------------------------

## 1. What the references teach about transitions, sound and music

These are measured facts. Other agents own the full teardowns, cited here; the ref3 notes are mine.

| ref | transitions | sound | music | what we take (re-skinned to ember, never copied) |
|---|---|---|---|---|
| **ref1** showreel, 73.8 s, 16:9 | 42 edits, median shot 1.57 s. Polarity strobes on whooshes, objects crossing the lens as the wipe, morphs, card carousels (`ref1_analysis.md` §2, §5.4) | dense: about 5 onsets/s, -14.2 LUFS, LRA 6.7, TP +0.3 (overs: we do better) | **127 BPM** (their comb fit, and my flux autocorrelation gives 127.5). A low-pass hold, then the drop on the first content cut | low-pass hold → drop on the reveal cut; a giant object crossing the lens as the wipe (= C7 / M6); a warm negative strobe at most twice |
| **ref2** "Creativity is...", 35 s, 9:16 | 14 worlds, median 2.88 s. **"Light is the transition"**: 7 of 13 transitions pass through near-black; bokeh blow-outs, light-ons, a whip, a light-leak wipe, a disintegration ending (`ref2_analysis.md` §2, §8) | **0.85 designed SFX/s**: 14 sub impacts, 16 air risers. Every world change gets a sub hit within ±0.15 s; every light event gets a riser that ends on it | **No measurable BPM**: a beatless ambient score. A mid-reel dip (RMS -25 dB at 16-17 s) = drop-out. Ends fading -27 to -33 dB (we will not fade, because of the loop rule) | light-born transitions (L1, L4, L7), J-cuts of 0.25-0.3 s, transitions in the VO gaps, sub-on-every-world-change, a beatless option for the most intimate reel |
| **ref3** "If you're dreaming of charging...", 21 s, 9:16 | about 1.5-2 s per scene. Diagonal light beam, an editorial panel sliding over a phone UI, a glass crystal macro with rack focus, film-frame overlays with edge text, blur-to-focus serif words (my 1.5 fps contact sheet) | not analysed in depth | **about 118 BPM** (my flux autocorrelation; low confidence) | the light-beam sweep (L7), a panel or card slide (D5), crystal + rack focus (C6 / M6), a film gate (L6) with **our own edge code** ("JAWAD · EMBER 800T"), never "KODAK PORTRA" or white paper frames |

Key consequence: two storytelling dialects exist, and the set should use both.
- (a) **Beat-gridded** reels (ref1/ref3: cuts on a 100-150 BPM grid).
- (b) **Breath-gridded** reels (ref2: no beat; cuts follow the VO phrases and light events).

For (b), `score.py` writes a beatless bed (drone + pad + risers), and the "grid" becomes the VO phrase map (Section 5.5).

---------------------------------------------------------------------------------------------------------------

## 2. Foundations: grid, easing, springs, blur, and the transition kit

### 2.1 Frame-locked tempos at 30 fps

frames per beat = 1800 / BPM, and frames per bar = 7200 / BPM. A BPM is **frame-locked** when beats (or at least bars) land on whole frames. Then picture cuts and audio hits can coincide exactly.

| BPM | f/beat | f/bar (s) | 8th (f) | 16th (f) | bars for 30-40 s → DUR | use |
|---|---|---|---|---|---|---|
| 72 | 25 | 100 (3.333) | 12.5 | 6.25 | 9 → 30.0, 10 → 33.3, 12 → 40.0 | grief, intimate confession |
| **75** | **24** | **96 (3.2)** | **12** | **6** | 10 → 32.0, **11 → 35.2**, 12 → 38.4 | emotional; fully locked to 16ths |
| 80 | 22.5 | 90 (3.0) | 11.25 | — | 11 → 33.0, 12 → 36.0, 13 → 39.0 | warm nostalgia |
| **90** | **20** | **80 (2.667)** | **10** | **5** | 12 → 32.0, **13 → 34.67**, 14 → 37.33, 15 → 40.0 | storytelling (default); fully locked |
| 96 | 18.75 | 75 (2.5) | 9.375 | — | 13 → 32.5, 14 → 35.0, 15 → 37.5 | lofi-hop storytelling |
| **100** | **18** | **72 (2.4)** | **9** | 4.5 | 14 → 33.6, **15 → 36.0**, 16 → 38.4 | cinematic drive, aspiration |
| **112.5** | **16** | **64 (2.133)** | **8** | **4** | 15 → 32.0, **16 → 34.13**, 18 → 38.4 | montage, craft reveal; fully locked |
| 120 | 15 | 60 (2.0) | 7.5 | 3.75 | 16 → 32, 18 → 36, 20 → 40 | upbeat, SaaS |
| **150** | **12** | **48 (1.6)** | **6** | **3** | 20 → 32.0, **22 → 35.2**, 24 → 38.4 | hype; the same grid as 75 (half-time ↔ double-time) |

- **The 75/150 trick:** one reel can open at 75 BPM (emotional, half-time) and *double* to 150 at the drop. The grid does not change: every 75-BPM beat is a 150-BPM beat. This is the cleanest "emotional → hype" switch.
- The grid functions every reel module defines (shared by the timeline, `cues()` and `score.py`):

```python
BPM, OFFSET = 90, 0.0                          # OFFSET = time of bar 0 beat 0 (usually 0.0 = frame 0)
HALF = 0.5 / 30
def B(n):   return OFFSET + n * 60.0 / BPM          # beat n -> s
def BAR(n): return B(4 * n)                         # bar n -> s
def q(t):   return round(t * 30) / 30               # quantise any time to a frame
def at(bar, beat=0, sub=0.0): return q(BAR(bar) + B(beat) - OFFSET + sub * 60.0 / BPM)   # "bar.beat" -> s
```

### 2.2 Easing vocabulary

The toolkit names are on the left. The cubic-bezier equivalents are for anyone working in After Effects or Premiere.

| name (`K.EASE[...]` or `K.ramp(..., ease)`) | ≈ cubic-bezier | job |
|---|---|---|
| `out_expo` | (0.16, 1, 0.3, 1) | arrivals, landings after a cut, B-side settles |
| `in_expo` | (0.7, 0, 0.84, 0) | accelerating **into** a cut: zoom-throughs, portals, push-ins |
| `inout_expo` | (0.87, 0, 0.13, 1) | **whips**: the velocity peak sits exactly at u=0.5, where the cut is |
| `inout_sine` | (0.37, 0, 0.63, 1) | fades, leak strength, tint bridges, focus breaths |
| `inout_cubic` | (0.65, 0, 0.35, 1) | camera repositions, rack focus, morphs |
| `out_cubic` | (0.33, 1, 0.68, 1) | brand keyword reveals (no bounce on brand type: kit rule), mask growth |
| `in_cubic` | (0.32, 0, 0.67, 0) | exits (exits ease out of view by accelerating) |
| `easy_ease` = `K.influence(80, 80)` | AE "easy ease 80 %" | slow cinematic camera moves, dolly-zoom |
| `glide` = `K.influence(90, 90)` | AE 90/90 | orbits, very smooth drifts |
| `K.bezier(x1, y1, x2, y2)` | custom | the "shown" curve in D4 (one curve drives both the display and the motion) |

**Pitfall (TOOLKIT §11.16):** `K.ramp(t, a, b)` defaults to `out_expo`. Always pass the ease. Fades use `'inout_sine'` or `'linear'`.
**Anticipation:** give big moves 2-4 frames of counter-motion (3-8 % of the move) before the main action (Disney principle, from the `video-motion-graphics` skill).
**Follow-through:** secondary elements settle 4-8 frames after the primary one.

### 2.3 Spring presets (`K.spring(t - t0, freq, damping)`)

| preset | freq Hz | damping | overshoot | settles (2 %) | use |
|---|---|---|---|---|---|
| SLAM | 3.2 | 0.45 | 20 % | 0.44 s (13 f) | type slams, crash zooms (`Glyphs.slam` defaults) |
| POP | 2.6 | 0.50 | 16 % | 0.49 s (15 f) | UI cards, chips, keycaps, B-window landing |
| SETTLE | 1.6 | 0.70 | 4.6 % | 0.57 s (17 f) | camera settle after a portal, premium reveals |
| SNAP | 3.0 | 0.55 | 12 % | 0.39 s (12 f) | playhead stopping on a marker |
| JELLY | 4.0 | 0.30 | 37 % | 0.53 s | comedy beats only; never on brand type |

Overshoot = e^(−ζπ/√(1−ζ²)), and the settling time ≈ 4/(ζ·2πf).

### 2.4 Motion blur and the cut rule

- `render_frame(draw, t, samples, shutter=0.5)` averages sub-frames across a 180° shutter (±1/120 s around t). Choose scene A or B with `t_i + HALF >= c`, where c is frame-quantised. Then frame n (t = c) is all-B and frame n−1 is all-A, and **blur never crosses a cut**.
- Sample policy: 3 default; 5 for 300-1500 px/s; 7 for whips, zoom-throughs, fly-throughs and shatter; and cap the spacing between samples at about 6 px (`saas-motion-styles`). For whips above ~200 px/frame, add `K.whip_blur(cv, min(0.5*v_px_per_frame, 900), angle)` after the scene draw. 0.5 = the shutter span, and it fills the gaps between samples.
- Keep 7 samples **inside the transition window only** (render cost is linear in samples, on 4 shared cores). Pattern: `def samples(t): return max([n for a, b, n in WINDOWS if a <= t <= b], default=3)`.
- Glitch transitions (D6, L6 judder) use **1 sample**: a glitch must stay discontinuous.

### 2.5 The shared transition kit `jawad_tx.py` [ADD] (owner: motion-toolkit-engineer)

All 43 recipes in Section 3 assume these helpers. A scene is a **pure function** `S(t, **cam_overrides) -> canvas` (linear premultiplied, H×W×4). A transition renders both scenes only inside its window, and computes masks at ¼ resolution.

```python
# jawad_tx.py  (import after jawad_kit)
import functools, math, numpy as np, cv2
import jawad_kit
from jawad_kit import K, T, ui, J
HALF = 0.5 / K.FPS
EMBERS = (K.C['FLAME'], K.C['RED'], K.C['AMBER'])          # leak/flare colours (linear)

def q(t): return round(t * K.FPS) / K.FPS
def side_b(t, c): return t + HALF >= c                     # True -> incoming scene
def mix_mask(a, b, m):                                     # premultiplied linear; m (H,W) or (H,W,1) in 0..1
    m = m[..., None] if m.ndim == 2 else m
    return a * (1.0 - m) + b * m
def up(m):  return cv2.resize(m, (K.W, K.H), interpolation=cv2.INTER_LINEAR)   # 1/4-res mask -> full
@functools.lru_cache(maxsize=1)
def grid4():                                               # 1/4-res pixel grid (cached; treat as read-only)
    Y, X = np.mgrid[0:K.H // 4, 0:K.W // 4].astype(np.float32) * 4.0
    return X, Y                                            # full-res px coordinates of each 1/4-res pixel
def zoom_canvas(cv, s, center=(K.CX, K.CY)):               # scale a finished canvas about a point
    M = np.float32([[s, 0, (1 - s) * center[0]], [0, s, (1 - s) * center[1]]])
    return cv2.warpAffine(cv, M, (K.W, K.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
def push(t, cuts, decay=16.0): return sum(K.impulse(t, c - 0.02, decay) for c in cuts)
def finish(cv, t, look, cuts=(), **kw):                    # the ONLY post call in a reel module
    p = push(t, cuts); b = K.LOOKS[look].get('bloom', 0.55)
    return K.post(cv, look, t, exposure=1.4 * p + kw.pop('exposure', 0.0), bloom=b * (1 + 0.9 * p), **kw)
@functools.lru_cache(maxsize=8)
def fbm(seed=0, scale=6.0, octaves=4):                     # static 1/4-res noise texture in 0..1 (read-only)
    rng = np.random.default_rng(seed); h, w = K.H // 4, K.W // 4; acc = np.zeros((h, w), np.float32); a = 1.0
    for o in range(octaves):
        n = rng.standard_normal((int(h / scale * 2 ** o) + 2, int(w / scale * 2 ** o) + 2)).astype(np.float32)
        acc += a * cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC); a *= 0.5
    acc = (acc - acc.min()) / (acc.max() - acc.min()); acc.flags.writeable = False; return acc
def sweep_mask(u, angle=35.0, soft=0.06):                  # band position identical to K.light_leak(sweep=u)
    X, Y = grid4(); a = math.radians(angle); dx, dy = math.cos(a), -math.sin(a)
    proj = (X - K.CX) * dx + (Y - K.CY) * dy; ext = abs(K.CX * dx) + abs(K.CY * dy)
    pos = (u * 2.6 - 1.3) * ext
    return up(np.clip((pos - proj) / (soft * ext * 2) + 0.5, 0, 1))   # 1 = already swept (show B)
def windows_samples(t, windows, default=3):
    return max([n for a, b, n in windows if a <= t <= b], default=default)
```

Rules every transition inherits:
1. B is **already running** (its clock started at least one window-length earlier), so it has no "first frame" pop.
2. Screen-locked content inside a portal or letter equals B's full-frame picture at the cut.
3. Masks are computed at ¼ res and upsampled.
4. All colour comes from palette tokens (`K.C['FLAME']`, `'RED'`, `'EMBER'`, `'AMBER'`, `'GOLD'`, `'SMOKE'`, `'IVORY'`). Never use raw hex.
5. Finishing always goes through `finish()` → `K.post(cv, LOOK, ...)`, with LOOK one of `'ember'`, `'noir_ember'` or a colorist `jw_*` look. The kit's post **crushes** the blacks (toe curve) and never lifts them.
6. A transition never contains readable copy that the brief has not verified.
7. UI text is ≥ 34 px after perspective. Safe zones: x 70-1010, y 230-1480.

---------------------------------------------------------------------------------------------------------------

## 3. Transition catalogue (43 transitions in 6 families)

Legend:
- ★ marks the **10 most premium for this brand**: C2, C3, M1, M6, Y1, Y5, L1, L4, L7, O6.
- ✂ marks the **5 editor-signature** transitions, the ones only an editor would make: D1, D2, D3, D4, D9.
- The SFX names are `audio.py` catalog names unless marked [ADD]; Section 4.8 specifies the [ADD] sounds.
- Gains are `gain_db` from the pre-balanced 0 dB: hero 0, layers -3 to -9, detail -10 to -14.
- `align='hit'` is the default. It puts the transient, the loudest pass, or the end of a riser/reverse swell on the cue time.

What the market is doing (dated evidence, Oct 2026):
- CapCut's own 2026 list of trending transitions is led by **speed-ramp "velocity" edits, beat-synced cuts, RGB/flicker glitches, cinematic push-ins/zooms and transformation cuts** ([CapCut help, 2026](https://www.capcut.com/help/capcut-transitions)).
- Motion design in 2026 is shifting from glossy to **handmade / film textures**: film-look overlays, collage, grain ([GraphicDesignJunction, Jan 2026](https://graphicdesignjunction.com/2026/01/video-and-motion-creative-trends-2026/)).
- Light leaks and lens flares are the most-downloaded transition effects in Uppbeat's 3M-creator library ([Uppbeat](https://uppbeat.io/blog/motion-graphics/video-transitions/the-most-downloaded-video-transition-effects)).
- Datamosh is "especially eye-catching in short-form" ([Adobe](https://adobe.com/uk/express/learn/blog/what-is-datamosh)).
- Instagram (April 2026) no longer recommends to non-followers accounts that mostly post content they did not make or *meaningfully transform*, so original craft is itself the distribution edge ([PetaPixel, 2026-04-30](https://petapixel.com/2026/04/30/new-instagram-policies-target-reposted-content/); [Planoly](https://www.planoly.com/blog/instagram-updates-its-original-content-policy.md)).
- Our read: trend-native moves (velocity, beat cuts, glitch) are table stakes. Jawad's edge is **light-born, ember-coloured, editor-meta transitions**, which nobody else's template pack has.

### 3.0 Allocating families across the 5-reel set

The playbook rule: no two reels share a signature device or a transition family. This allocation is a suggestion; the creative director's look matrix decides.

| reel archetype (from the concept panel) | transition family | its signature (★/✂) | glue allowed everywhere |
|---|---|---|---|
| emotional confession / memory | **Light & film** (L) | L4 halation bloom-out or L1 light-leak burn | hard beat cut + L3 exposure push; J-cuts; Y5 underline as an underline only (not as a wipe) |
| editor POV / client story | **Digital / editor-native** (D) | D1 playhead scrub or D9 Ctrl+Z rewind | same |
| manifesto / hype | **Type-driven** (Y) | Y1 zoom through the serif counter or Y3 slam cuts | same |
| journey / nostalgia / origin | **Camera** (C) + **match** (M) | C3 portal push-through or M1 circle match cut | same |
| transformation / before-after | **Organic** (O) + morph | O6 ember disintegration or O4 shatter | same |

Y5 (underline-stroke wipe) is the brand's own mark. Use it as a full transition in at most **one** reel, where it is that reel's signature; elsewhere it only underlines.

### 3.1 Summary table

| ID | name | family | frames @30 | core ease | samples | paired SFX (catalog) | grid placement | flag |
|---|---|---|---|---|---|---|---|---|
| C1 | whip pan (h/v) | camera | 8 (10-12 at 75 BPM) | inout_expo | 7 + whip_blur | whip / whoosh_fast | pass = beat | |
| C2 | dolly-zoom (Vertigo) | camera | 36-60 | easy_ease | 3-5 | whoosh_slow + reverse_swell + sub_drop | end = bar line | ★ |
| C3 | push-in through object (portal) | camera | 18-30 + 8 settle | in_expo → out_expo | 7 last 10 f | reverse_swell + air_zoom + impact_soft | cut = downbeat | ★ |
| C4 | 3D fly-through (z-space tunnel) | camera | 18-30 per surge | surge + exp brake | 7 | whoosh_by ×n + slot_tick + reverse_swell | passes on 8ths, brake on downbeat | |
| C5 | orbit reveal | camera | 30-45 | glide | 5-7 | whoosh_slow + glass_tap + shimmer | edge-on = bar line | |
| C6 | rack-focus hand-off | camera | 12-24 | inout_cubic | 3 | (ui_hover −12) / none | arrival = beat | |
| C7 | parallax push + foreground wipe | camera | 15-24 | inout_cubic | 5 | whoosh_fast | FG cover = beat | |
| C8 | crash / snap zoom | camera | 3-4 + 6 settle | out_expo | 5 | whip + impact_soft (+ sub_drop) | beat, or the "and" for comedy | |
| M1 | shape match cut (circle) | match | 0 (12-18 each side) | in_cubic / out_expo | 3-5 | tonal glass_tap or [ADD] tabla_na + impact_soft | downbeat | ★ |
| M2 | colour match / hue bridge | match | 8-16 | sin² bridge | 3 | reverse_swell + shimmer | beat 1/3 | |
| M3 | motion match (momentum cut) | match | 0 (6-10 each side) | in_cubic → out_cubic | 7 near cut | whoosh_fast + card_slide | beat | |
| M4 | frame-in-frame (rectangle) match | match | 18-24 | in_expo → out_expo | 7 last 8 f | glass_tap + air_zoom (+ ui_click) | downbeat | |
| M5 | morph cut (shape morph) | match | 12-20 | inout_cubic + POP | 3-5 | shimmer + swish_small (or [ADD] sitar_meend) | end = beat | |
| M6 | object carry-over (ember / crystal / cursor) | match | 12-30 | inout_cubic path | 7 near cut | whoosh_by (doppler) + sparkle / glass_tap | fastest point = beat | ★ |
| Y1 | zoom through a serif counter | type | 18-24 | in_expo (vt.zoom) | 7 | reverse_swell + air_zoom (+ sub_drop) | cut = the drop downbeat | ★ |
| Y2 | light-sweep text-wipe | type | 14-24 | inout_sine | 3-5 | shimmer + whoosh_fast | core crosses centre = beat | |
| Y3 | kinetic slam cuts | type | 6-20 per word | SLAM spring | 3 | impact_soft ×n + impact_big/sub_drop last | every slam on beat or 8th | |
| Y4 | glyph-mask bloom reveal | type | 20-36 | out_cubic | 3 | shimmer + whoosh_slow + impact_soft | complete = downbeat | |
| Y5 | underline-stroke wipe (house mark) | type | 10 draw-on + 12-16 wipe | out_cubic → inout_expo | 5 | [ADD] ember_stroke + whoosh_fast + impact_soft | draw-on on beat, cover on next beat | ★ |
| Y6 | scramble-decode cut | type | 15-21 | stepped (scramble) | 3 | typing / glitch_short + ui_tick + check_ding | resolve = beat | |
| L1 | light-leak burn (ember) | light | 12-20 (24-36 dreamy) | built-in sin envelope | 3 | reverse_swell + shimmer (or flash_hit −6) | cut = downbeat / beat 3 | ★ |
| L2 | film burn | light | 18-30 | in_cubic → in_expo | 3 | [ADD] film_burn (+ downlifter) | full burn = downbeat | |
| L3 | exposure-push flash frame | light | 2-4 | impulse decay 16 | 3 | flash_hit (+ sub_drop) / camera_shutter | on beat | glue |
| L4 | halation bloom-out wipe | light | 16-24 | sin² | 3 | shimmer + reverse_swell | cut = beat 1 | ★ |
| L5 | anamorphic flare wipe | light | 10-16 | inout_cubic | 5 | whoosh_fast + shimmer + sparkle | core at centre = beat | |
| L6 | projector / film-gate slip | light | 6-10 slip + 1 bar judder | step (24 fps cadence) | 1-3 | [ADD] projector_rattle + camera_shutter | slip = downbeat | |
| L7 | light-beam (god-ray) sweep | light | 18-30 | inout_sine | 3-5 | whoosh_slow + shimmer (+ harmonium swell) | beam at centre = downbeat | ★ |
| L8 | aperture iris close/open | light | 8 + 2 + 10 | in_cubic / out_back | 3 | camera_shutter + ui_click + reverse_swell | black frames on a beat | |
| D1 | timeline playhead scrub | editor | 36-60 | inout_expo + SNAP | 3-5 | [ADD] scrub + ui_tick + ui_click | stop = downbeat | ✂ |
| D2 | razor-tool cut | editor | 6-10 + 1 + 8-12 | out_expo | 5 | [ADD] razor_snip + card_slide (music gated) | click on beat 4 | ✂ |
| D3 | render-progress-bar wipe | editor | 30-60 + 8 | stepped Track, out_expo tail | 3 | bar_grow + ui_tick + toast_chime | 100 % = downbeat | ✂ |
| D4 | keyframe-graph swoosh | editor | 10 + 14-20 | the displayed bezier | 5-7 | pop ×n + swish_small + whip | keys on 8ths, steepest = beat | ✂ |
| D5 | UI window swap (SaaS) | editor | 12-18 | in_cubic exit / POP enter | 5 | whoosh_fast + card_slide + glass_tap | landing = beat | |
| D6 | glitch / datamosh-lite | editor | 6-12 | stepped (hold 2 f) | 1 | glitch_short + [ADD] data_crunch | start on the "and", resolve on beat | |
| D7 | RGB-split chroma shock | editor | 2-4 | impulse decay 20 | 3 | glitch_short + whip | beat / 8th | |
| D8 | speed-ramp (velocity) cut | editor | 10-16 | in_expo / out_expo time-warp | 7 | whoosh_fast + riser(0.35) + impact_soft | cut = beat | |
| D9 | undo / Ctrl+Z rewind | editor | 6 + 18-30 + 2 | in_cubic (reverse) | 5 | typing(n=2) + [ADD] tape_rewind + impact_soft (music tape-stop) | press beat 4, restore downbeat | ✂ |
| O1 | ink bleed | organic | 30-45 | out_cubic | 3 | [ADD] ink_bloom + whoosh_slow | drop = downbeat | |
| O2 | smoke wipe | organic | 24-36 | inout_sine | 3 | whoosh_slow + night_air swell + impact_soft | clear = downbeat | |
| O3 | page tear (black paper) | organic | 12-20 | in_cubic / out_expo | 5 | [ADD] paper_tear + card_slide | tear end = beat | |
| O4 | shatter | organic | 15-24 (+10 slow-mo) | ballistic | 7-9 | [ADD] glass_shatter + sub_drop + impact_big | impact = downbeat | |
| O5 | molten pour | organic | 24-36 | in_cubic + exp cool | 3-5 | [ADD] molten_pour + bubble_pop + impact_soft | cover = downbeat | |
| O6 | ember disintegration | organic | 30-45 | inout_sine front | 3-5 | [ADD] ember_crackle + whoosh_slow → silence → impact_big | start on beat, reveal next downbeat | ★ |

---------------------------------------------------------------------------------------------------------------

### 3.2 CAMERA family

#### C1 · Whip pan (horizontal, or vertical "swipe-whip")
- **Feel / when:** energy, "meanwhile", time jumps, snapping between two ideas of equal weight. The **vertical** whip mirrors the swipe gesture of 9:16 feeds. Never use it on grief beats. Classic usage: action, suspense, time jumps, comedic reveals ([Nikon editing tips](https://www.nikon.co.uk/en_GB/learn-and-explore/magazine/tips-and-tricks/cut-to-the-chase-10-tricks-to-add-pace-and-energy-to-your-edits)).
- **Timing:** 8 frames at 90-150 BPM (4 out + 4 in). At 75 BPM use 10-12 frames. The cut sits at u = 0.5.
- **Ease:** camera yaw (or pitch for vertical) follows `inout_expo` across the window, so the velocity peaks on the cut. Optional anticipation: 2 frames of 1.5° counter-yaw.
- **Blur:** 7 samples plus `K.whip_blur(cv, min(0.5*v, 900), angle=0 or 90)`, where v = px/frame (≈ Δyaw_rad × focal 1500).
- **Build:**
```python
def tx_whip(t, c, A, B, d=8/30, deg=32.0, axis='yaw', sign=1):
    u = K.clamp((t - (c - d / 2)) / d)
    def ang(tt):
        uu = K.clamp((tt - (c - d / 2)) / d)
        return sign * deg * (K.EASE['inout_expo'](uu) - (1.0 if side_b(tt, c) else 0.0))   # A: 0->+deg, B: -deg->0
    a = ang(t)
    cv = (B if side_b(t, c) else A)(t, **{axis: a})          # scene builds Cam(..., yaw=a) / pitch=a
    v = abs(ang(t + 1 / K.FPS) - a) * math.pi / 180 * 1500   # px per frame at the image centre
    return K.whip_blur(cv, min(0.5 * v, 900.0), 0.0 if axis == 'yaw' else 90.0)
```
  Rotating the 3D camera gives real parallax: near embers streak more than the far haze. For 2D plates, offset the plate by ±1.4 W instead.
- **SFX:** `whip` hit at c, gain -3, `params=dict(direction=sign)`, `pan=0.4*sign`. At 75 BPM use `whoosh_fast` (pass 0.42 s) instead. Add `impact_soft` -6 at c only when landing on a downbeat. A montage of whips: `A.on_beats('whip', BPM*2, beats, gain_db=-4, pan=lambda b: 0.4*(-1)**b)`.
- **Grid:** the pass/cut on a beat (montage: 8ths), so the whip starts d/2 before the beat.
- **Watch:** at most 3 whips in a row. With 7 samples, a 32° yaw over 4 frames is about 210 px per frame, so `whip_blur` is mandatory to hide the stepping.

#### C2 · Dolly-zoom (Vertigo) ★
- **Feel / when:** realisation and dread, the "duniya ruk gayi" moment ("everything stopped"). The world stretches while Jawad stays the same size. Use it once per reel at most, on his 2.5D cut-out (shocked or neutral sheet expression). It is the textbook shot for inner panic and realisation: Hitchcock's *Vertigo*, Spielberg's *Jaws* beach shot ([search summary of Nikon/Wolfcrow](https://wolfcrow.com/the-3-important-in-camera-transitions-in-filmmaking/)).
- **Timing:** 36-60 frames (1.2-2.0 s). Used as a transition, the world swap happens at peak stretch (u ≈ 0.85).
- **Ease:** `easy_ease` on the distance. Focal = F0·D/D0 keeps the subject size constant.
- **Blur:** 3, then 5 for the last 12 frames (the edges move fast).
- **Build:**
```python
def dolly_cam(t, t0, t1, D0=1500.0, D1=640.0, subj_z=0.0):
    u = K.EASE['easy_ease'](K.ramp(t, t0, t1, 'linear'))
    D = K.lerp(D0, D1, u)                                     # push in (use D0=640 -> D1=1800 for a pull)
    return K.Cam(pos=(0, 0, subj_z - D), focal=1500.0 * D / D0, focus_dist=D, aperture=K.lerp(18, 46, u))
# The world needs REAL depth: haze billboards at z = 2500..6000, J.embers(...), props at several z. A flat
# backdrop shows nothing. The cut-out of Jawad is a plane at z = subj_z (face-compositor sprite).
# As a transition: at u >= 0.85 swap world A -> world B behind the same cut-out, hidden by an L1 leak or an
# L3 exposure push. Same man, new world.
```
- **SFX:** `whoosh_slow` hit at the stretch peak, -6. `reverse_swell(duration=t1-t0)` ending at t1, -4. `sub_drop` at t1, -3. Optional `heartbeat(n=2, bpm=BPM)` under it at -6. Music: the pad low-pass sweeps 2400 → 400 Hz across the move, and a ½-beat drop-out at t1 (Section 4.4).
- **Grid:** t1 on a bar downbeat; t0 = t1 − 2 or 4 beats.

#### C3 · Push-in through an object (portal) ★
- **Feel / when:** entering a memory, an idea, or "the inside of the edit". Curiosity, and premium continuity. Portals on brand: the camera lens of a Blender camera prop, the glass crystal, the flame "J" ring mark, a monitor or phone screen, the play-button ring of the OpenArt cover idea.
- **Timing:** 18-30 frames approach + cut at full fill + 8 frames settle in B.
- **Ease:** the camera's z uses `in_expo` (bezier 0.7, 0, 0.84, 0). B settles with scale 1.08 → 1.0 `out_expo`.
- **Blur:** 7 for the last 10 frames, plus `K.zoom_blur(cv, 0.10*in_cubic(u))` fading out over u 0.9 → 1.
- **Build:**
```python
def tx_portal(t, c, A, B, P=(0.0, -40.0, 0.0), r_world=260.0, L=24 / 30):
    if side_b(t, c):
        return zoom_canvas(B(t), K.lerp(1.08, 1.0, K.ramp(t, c, c + 8 / 30, 'out_expo')))
    u = K.ramp(t, c - L, c, 'linear'); e = K.EASE['in_expo'](u)
    cam = K.Cam(pos=(0.0, 0.0, K.lerp(-1500.0, P[2] - 30.0, e)), aperture=24)
    cv = A(t, cam=cam)
    xy, d = cam.project(np.array([P], np.float64)); R = r_world * cam.focal / d[0]
    X, Y = grid4()
    m = up(np.clip((R - np.hypot(X - xy[0, 0], Y - xy[0, 1])) / 3.0 + 0.5, 0, 1))   # 3 px AA aperture
    cv = mix_mask(cv, B(t), m)                                  # B is SCREEN-LOCKED: at fill it IS B's frame
    K.zoom_blur(cv, 0.10 * K.EASE['in_cubic'](u) * (1 - K.ramp(u, 0.9, 1.0, 'linear')))
    return cv
```
  For non-circular portals, rasterise the projected aperture polygon with `ui.fill_mask` instead of the circle. Draw the portal object's rim (lens barrel, crystal facets) **over** the mask so the aperture has thickness.
- **SFX:** `reverse_swell(duration=L)` ending at c, -3. `air_zoom` hit at c, 0. `impact_soft` at c, -6 (intimate) or `sub_drop` -6 (epic). Music: a new section enters on c.
- **Grid:** c = a bar downbeat; the approach starts 1-1½ beats before.

#### C4 · 3D fly-through (z-space tunnel of frames, cards or words)
- **Feel / when:** time compression ("5 saal, 2000 edits": five years, 2000 edits), a journey, overwhelm, a career montage. It is the ref1 "nested frames" energy re-done as a tunnel of **Jawad's own frames**.
- **Timing:** 18-30 frames per surge, then a 10-frame brake.
- **Ease:** surge-then-exponential-brake, so the velocity stays continuous (the card-tunnel recipe):
  `z = -1500 + V0·(a + 0.3·L/π·(1 − cos(π·a/L)))`, then `+ V0/6·(1 − e^(−6(t − T1)))`. Roll 0 → 34° `out_cubic`.
- **Blur:** 7 throughout.
- **Build:** the "Card tunnel" recipe in `saas-motion-styles/recipes.md`, re-skinned. Use `ui.glass_card(480, 624, r=36, look='ember')` with `ui.media_face(card, frame)`, on a golden-angle helix, with depth fog `K.smoothstep(7800, 5600, depth)`. For a **type tunnel**, put `T.render(word, 'jw_caps', px=120)` planes at z steps of 900 and make the last one the `'jw_key'` keyword.
- **SFX:** `whoosh_by` on each beat (`params=dict(dur=1.4, direction=±1)`, pan alternating ±0.5, -6). `slot_tick` `align='start'`, `params=dict(dur=tunnel_len)`, -12. `reverse_swell` ending on the title slam, -4. Exit: `impact_soft` (intimate) or `impact_big` (epic).
- **Grid:** each frame passes the lens on an 8th; the brake ends on a downbeat.

#### C5 · Orbit reveal
- **Feel / when:** "dusra pehlu" (the other side of the story), revealing what is behind or around a hero object, contemplation.
- **Timing:** 30-45 frames.
- **Ease:** `glide` (influence 90/90).
- **Blur:** 5, rising to 7 while an occluder crosses the lens.
- **Build:** two variants.
  - **(a) Card flip-orbit:** `cam = K.Cam.orbit(target, K.lerp(1700, 900, e), yaw=K.lerp(-25, 155, e), pitch=K.lerp(6, 0, e), aperture=30)`. The card shows face A while `dot(card_normal, cam.forward) < 0`, otherwise face B (`ui.media_face(card, B(t))`). The swap happens edge-on at yaw ≈ 90°. End with a C3-style push so B fills the frame.
  - **(b) Occlusion orbit:** the camera arcs past a big foreground object (the 3D crystal, Jawad's shoulder cut-out). Swap the background when the occluder covers more than 70 % of the frame (measure the alpha coverage of its sprite).
- **SFX:** `whoosh_slow` pass at edge-on, -4. `glass_tap` at edge-on, -8, with `params=dict(pitch=...)` in key. `shimmer` on the reveal, -6. Music: a chord change at the swap.
- **Grid:** edge-on = beat 1 of a bar; the orbit starts one bar earlier.

#### C6 · Rack-focus hand-off (and the "blur-swap")
- **Feel / when:** shifting attention ("lekin asal baat ye thi...", "but the real thing was..."), intimacy. The softest transition; it lives happily under VO with no SFX. Ref2 does this with type (blur-in and blur-out), and ref3 with the crystal.
- **Timing:** 12-24 frames. The blur-swap is 8-10 frames out + 8-10 frames in.
- **Ease:** `inout_cubic` on `focus_dist`. Aperture 40-70.
- **Blur:** 3.
- **Build:** `cam = K.Cam(aperture=60, focus_dist=K.lerp(d_fg, d_bg, K.ramp(t, t0, t1, 'inout_cubic')))`, with FG and B content at their own depths in one `K.Scene`. **Blur-swap:** rack everything to `focus_dist=200` (fully soft), switch scene A → B at maximum defocus, then rack back. An invisible cut. On type: `ts.draw_plane(..., blur=K.lerp(70, 0, ramp))` (ref2's "blown bokeh rack-focus reveal").
- **SFX:** none, or `ui_hover` -12. The music breathes (a pad swell or a harmonium bellows).
- **Grid:** focus arrives on a beat; the blur-swap midpoint sits on a beat.

#### C7 · Parallax push + foreground wipe
- **Feel / when:** depth and presence for the 2.5D cut-outs; "stepping into the scene"; storytelling glue. The ref1 "giant object crossing the lens" in ember: a clapperboard, a film strip, a monitor edge, a dark pillar.
- **Timing:** 15-24 frames.
- **Ease:** camera dolly `inout_cubic` 0 → +350 world units, and yaw 0 → 4°.
- **Blur:** 5.
- **Build:** layers at z = −350 (FG object: huge DOF blur at aperture 40), 0 (Jawad's cut-out) and +2500 (haze). The FG object sweeps across and covers 100 % of the frame for 2-3 frames. Cut under it; B starts with the same object leaving the other side. Measure the coverage with the FG sprite alpha (≥ 0.97 on the cut frame).
- **SFX:** `whoosh_fast` pass at c, -4, panned in the FG's direction. Optional `impact_soft` -10 on landing.
- **Grid:** the full cover on a beat.

#### C8 · Crash / snap zoom
- **Feel / when:** shock, punchline, emphasis. Use the "shocked" or "smirk" sheet expressions. Comedy or hype only.
- **Timing:** 3-4 frames of zoom (scale 1 → 1.35) + hold. As a transition it ends in a hard cut to B, which settles 1.2 → 1.0 over 6 frames `out_expo`.
- **Ease:** `out_expo`. Hit judder: a damped sub-pixel offset (TOOLKIT §11.15: `K.shake` alone peaks at about 2 px).
- **Blur:** 5.
- **Build:** `cv = zoom_canvas(A(t), K.lerp(1.0, 1.35, K.ramp(t, c - 4/30, c, 'out_expo')), center=face_xy)` + `K.zoom_blur(cv, 0.05*K.impulse(t, c-4/30, 12))`.
- **SFX:** `whip` (direction 1) hit at c − 1 frame, -6, plus `impact_soft` at c, 0. Epic: add `sub_drop` -6. Comedy: [ADD] `record_scratch` instead of the impact.
- **Grid:** on a beat; comedy lands on the "and" (syncopated surprise).

### 3.3 MATCH / MORPH family

#### M1 · Shape match cut (the circle family) ★
- **Feel / when:** a poetic link that shows the "editor's eye". It makes people rewatch and send. The textbook case is the *2001* bone → spacecraft graphic match ([match-cut glossary](https://screendollars.com/glossary/m/match-cut)).
- **Jawad's circles:** the record dot ● on a camera, the flame "J" ring mark, the play-button ring, a lens, the sun disc, a tabla head (desi!), a chai cup seen from above, an eye's iris.
- **Timing:** a hard cut with 12-18 frames of pre-move (A pushes toward the match pose) and 12-18 frames of post-move (B pulls away). Optional 2-frame L3 push.
- **Ease:** A `in_cubic` toward the pose; B `out_expo` away from it. Perceived motion continues through the cut.
- **Blur:** 3-5. Never sampled across the cut (HALF rule).
- **Build:** a shared constant `MATCH = dict(x=540, y=820, r=250)`. Each scene exposes `circle_pose(t)`, and the camera/scale is solved so that at c−1f and c both circles sit on MATCH (centre within 2 px, radius within 2 %). QA: `cv2.HoughCircles` on frames c−1 and c.
- **SFX:** one **tonal** hit in key: `glass_tap` with `params=dict(pitch=…)`, or [ADD] `tabla_na` tuned to Sa, at 0 dB. Plus `impact_soft` -8. Music: a section change on c (a new instrument enters).
- **Grid:** c on a bar downbeat.

#### M2 · Colour match / hue bridge
- **Feel / when:** mood continuity across time and place. The orange of a 3 AM monitor becomes the orange of a sunrise: hope. A red "REC" dot becomes a red sunset ([colour-match idea](https://www.studysmarter.co.uk/explanations/media-studies/filmmaking/match-cut/)).
- **Timing:** 8-16 frames.
- **Ease:** tint k = sin²(πu) (an `inout_sine` shape), with the cut at u = 0.5.
- **Blur:** 3.
- **Build:** `L = K.lum(cv[..., :3])[..., None]; cv[..., :3] = cv[..., :3]*(1-k) + L*K.C['FLAME']*1.6*k` on both sides, plus `finish(..., exposure=0.4*k)`. It works best when A ends on a dominant FLAME highlight and B starts on one.
- **SFX:** `reverse_swell(duration=0.3)` ending at c, -6, and `shimmer` -10. Music: a common-tone pivot (one pad note holds across the chord change).
- **Grid:** c on beat 1 or 3.

#### M3 · Motion match (momentum cut)
- **Feel / when:** unstoppable progress, "safar" (journey), a hand-off between chapters.
- **Timing:** a 0-frame cut at maximum velocity, with 6-10 frames of motion on each side.
- **Ease:** shared screen-space velocity. A uses `in_cubic` into the cut; B continues, then `out_cubic` to rest.
- **Blur:** 7 near the cut.
- **Build:** one `MOVE = K.Track([(c - 0.3, (140, 900), 'in_cubic'), (c, (540, 900), 'out_cubic'), (c + 0.3, (940, 900))])`. The two segments cover equal distance, so the velocity is continuous at c: 3 × 400/0.3 px/s on both sides of the cut. Both scenes draw their moving object at `MOVE(t)` (same direction, speed and screen y).
- **SFX:** `whoosh_fast` pass at c, -3, panned by direction. `card_slide` "thup" at the stop, -8.
- **Grid:** c on a beat; the stop on the next beat.

#### M4 · Frame-in-frame (rectangle graphic match)
- **Feel / when:** "screen → life": the phone feed becomes the real world, or the edit monitor becomes the final film. Editor POV. Ref2 uses an inset "program monitor" card (`ref2_analysis.md` device 11).
- **Timing:** 18-24 frames push + cut.
- **Ease:** `in_expo` push; B 1.05 → 1.0 `out_expo`.
- **Blur:** 7 for the last 8 frames.
- **Build:** C3 with a rectangle. The `ui.app_window(look='ember', title='', header='')` slot or a `ui.glass_card` + `ui.media_face(card, B(t))` (B screen-locked). Solve the camera distance so the slot spans exactly 1080×1920 at c: `dist = slot_w_world*focal/1080`. The comet rim (`face_at(sweep=...)`) fades out over the last 4 frames.
- **SFX:** `glass_tap` at the push start, -8. `air_zoom` hit at c, 0. `ui_click` -10 if a cursor click triggers the full screen.
- **Grid:** c on a downbeat.

#### M5 · Morph cut (shape morph)
- **Feel / when:** transformation. A struggle line becomes a growth graph; **Jawad's orange underline morphs into a timeline playhead**, an audio waveform, an ECG heartbeat line or a road.
- **Timing:** 12-20 frames.
- **Ease:** `inout_cubic` on the morph, then a POP spring settle.
- **Blur:** 3 (5 if fast).
- **Build:** resample both polylines to N = 256 points by arc length, then `pts = (1-e)*Pa + e*Pb`. Stroke with `ui.stroke_mask([(pts, False)], K.W, K.H, width=K.lerp(wa, wb, e))`, colour `K.C['AMBER']*0.5 + K.C['FLAME']*1.5`, and glow via `K.gblur` of the mask (σ 4/12/30, added). The background cross-dissolves under the line (`inout_sine`, 8 frames). The line carries the eye.
- **SFX:** `shimmer` at the start, -8, and `swish_small` along the move, -10. Desi option: [ADD] `sitar_meend` (a glide up a 4th) as the morph sound.
- **Grid:** the morph ends on a beat.

#### M6 · Object carry-over (ember spark / glass crystal / cursor) ★
- **Feel / when:** one continuous "chingari" (spark) travels through the chapters of a life. It is the most premium continuity device when the object is one consistently lit 3D asset ([ADD] Blender crystal in `assets3d_jawad.py`) or a single bright ember from `J.embers`.
- **Timing:** the object travels 12-30 frames. Cut the background under it at its fastest point.
- **Ease:** a Catmull-Rom or `K.Track` path with `inout_cubic`.
- **Blur:** 7 near the cut.
- **Build:** draw the carrier in **screen space after** each scene draw: `K.draw(cv, spark_glow, *path(t), scale=s(t), mode='add')` (glow built once with `K.glow(K.disc(10, K.C['AMBER']*3), K.C['FLAME'], (6, 18, 50), 1.3)`). A 3D crystal uses `S3.get('<crystal>', '<variant>', mode='spin').at_yaw(ang(t))`. Interactive light: add `K.radial(700, K.C['FLAME']*0.25)` at `path(t)` in both scenes, so the object lights both worlds.
- **SFX:** `whoosh_by` (`params=dict(dur=…, direction=±1)`) with its hit at the fastest point and `pan=(x_pass-540)/540`, -4. On landing: `sparkle` or `glass_tap` -8. For an ember: an [ADD] `ember_crackle` trail at -12.
- **Grid:** the fastest point on a beat; the landing on the next downbeat.

### 3.4 TYPE-DRIVEN family

House type: `'jw_key'` (Instrument Serif Italic, amber → flame → red), `'jw_caps'` / `'jw_caps_bold'` (Poppins caps), `'jw_mono'`, and `J.HouseTitle`. Width ≤ 940 px (≤ 780 px in y 1050-1700). Measure with `T.measure(text, 'jw_key', px=...)`.

#### Y1 · Zoom through a letter / serif counter ★
- **Feel / when:** entering the meaning of a word. "SAPNA" (dream) → inside the counter of its "a" sits the childhood room. This is the signature move of cinematic kinetic type (ref2's world), done in Jawad's own serif.
- **Timing:** 18-24 frames of zoom, landing on B's full-frame shot.
- **Ease:** `vt.zoom(u, zp, x, y, s0=1.0, s1=46.0, ease='in_expo')` + `K.zoom_blur(cv, 0.12*in_cubic(u)*(1 - ramp(u, .92, 1)))`.
- **Blur:** 7 during the zoom.
- **Build:** the `recipes.md` "Video-in-type with zoom-through" pattern, with the brand serif:
```python
vt = T.VideoType(word, px=230, tracking=-0.01, look='dark')     # footage/scene B inside the letters
zp = vt.zoom_point('a', index=word.index('a'), kind='counter')  # Instrument Serif Italic counters are narrow:
                                                                # test 'o', 'a', 'd', 'e', pick the widest
# t < VZ0: vt.draw(cv, B_frame, 540, 900, sweep=...)  ;  VZ0..VZ1: vt.draw(cv, B_frame, **vt.zoom(u, zp, 540, 900))
```
  B is screen-locked inside the letters, so at VZ1 it *is* the full-frame shot. [ADD] if needed: a `'jw_key'`-matched rim (`rim_style=` FLAME → RED) on `VideoType`. Check that the counter fill reads at 46× (no aliasing: draw the counter mask from a 2× raster).
- **SFX:** `reverse_swell(duration=VZ1-VZ0)` ending at VZ1, -3. `air_zoom` hit at VZ1, 0. Optional `sub_drop` -6. Music: **the drop** (the first full-band bar) lands on VZ1.
- **Grid:** VZ1 = a downbeat (the drop bar).

#### Y2 · Light-sweep text-wipe
- **Feel / when:** a promise word revealed with polish ("PERSONAL BRAND"). Mid-energy.
- **Timing:** 14-24 frames.
- **Ease:** sweep u `inout_sine`. The scene edge follows the band core.
- **Blur:** 3-5.
- **Build:** for the first ~40 % of the window the sweep runs on the word: `ts.draw(cv, x, y, sweep=u1, sweep_kw=dict(color='AMBER', width=0.09, angle=-32))`. Then the same band continues across the frame: `K.light_leak(cv, t, colors=EMBERS, strength=1.1, sweep=u2, angle=-32)`. B is composited behind it with `mix_mask(A, B, sweep_mask(u2, angle=-32))`, which tracks the leak band exactly.
- **SFX:** `shimmer` hit at the sweep start, -6. `whoosh_fast` pass when the core crosses the centre, -6.
- **Grid:** the core crosses the frame centre on a beat.

#### Y3 · Kinetic slam cuts (one word per beat)
- **Feel / when:** conviction, a manifesto, a list of truths ("Hook. Story. Edit. Sound."). Hype.
- **Timing:** one word per beat (20 frames at 90 BPM) or per 8th (6 frames at 150 BPM).
- **Ease:** `T.Glyphs(word, 'jw_caps_bold', px=…).slam(cv, t, x, y, t0=b, s0=1.6, dur=0.45, freq=3.2, damping=0.45)` (SLAM preset). The `'jw_key'` keyword gets the premium rise instead (no bounce on brand type).
- **Blur:** 3. `Glyphs.slam` smears itself. Use `smear=False` once a word has settled (TOOLKIT §10).
- **Build:** `WORDS = [(word, beat)]`. The background alternates among 2-3 plates with each slam (a hard cut, HALF-early), plus `finish(..., cuts=slam_times)` (exposure push) and a damped sub-pixel judder.
- **SFX:** `impact_soft` 0 on each slam (vary the seeds automatically; pan alternating ±0.15). The last word gets `riser` ending on it -4, `impact_big` 0 and `sub_drop` -4. Under VO, every slam aligns to the **stressed syllable** (faster-whisper word times).
- **Grid:** every slam on a beat or 8th; the last one on a downbeat.

#### Y4 · Glyph-mask bloom reveal
- **Feel / when:** "ek idea → poori film" (one idea → a whole film). The keyword becomes a window into the next world, then *becomes* that world.
- **Timing:** 20-36 frames.
- **Ease:** mask radius `out_cubic` 0 → 1400 px; word scale 1 → 1.15.
- **Blur:** 3.
- **Build:**
```python
@functools.lru_cache(maxsize=4)
def glyph_dist(word, px):                                    # outside-distance of the keyword mask, 1/2 res
    ts = T.render(word, 'jw_key', px=px)                     # placed exactly as it is drawn on screen
    m = (cv2.resize(full_frame_alpha(ts), (K.W // 2, K.H // 2)) < 0.5).astype(np.uint8)
    return cv2.distanceTransform(m, cv2.DIST_L2, 5) * 2.0                  # full-res px
r = 1400 * K.EASE['out_cubic'](u); d = up2(glyph_dist(word, px)) + 40 * up(fbm(3))
m = np.clip((r - d) / 6.0, 0, 1)                             # organic grow from the letters
cv = mix_mask(A_t, B_t, m); edge = np.exp(-((d - r) / 10.0) ** 2)[..., None]
cv[..., :3] += edge * K.C['FLAME'] * 2.2 * (1 - u)           # emissive flame edge, fades as it finishes
```
  [ADD] `full_frame_alpha` (draw the text sprite into an empty canvas) and `up2` (½-res upsample).
- **SFX:** `shimmer` at the start, -6. `whoosh_slow` pass at the middle, -6. `impact_soft` on completion, -8. Music: the pad opens (LP 600 → 2400 Hz) across the reveal.
- **Grid:** completion on a downbeat.

#### Y5 · Underline-stroke wipe (the house mark becomes the transition) ★
- **Feel / when:** instant brand recognition. Jawad's glowing orange underline (his covers) draws on under the keyword, keeps going, thickens, and sweeps the frame into the next scene.
- **Timing:** draw-on 10 frames, then the wipe 12-16 frames.
- **Ease:** draw-on `out_cubic` (`J.underline(760).draw(cv, x0, y, u)`). Wipe: the stroke width `K.lerp(7, 2600, inout_expo(u2))` while it rotates −4° → −30° and its centre rises 300 px.
- **Blur:** 5 during the wipe. Pass `smear=` px per shutter to `ul.draw` during a fast draw-on.
- **Build:** draw-on with the kit's `J.underline`. For the wipe, the stroke becomes a capsule mask `ui.stroke_mask([(pts, False)], K.W, K.H, width=w(t))` on a gently arced 2-point path. Inside the mask: B. On its ~30 px leading band: emissive `K.C['AMBER']*0.5 + K.C['FLAME']*2.5`, plus a gblur glow (σ 8/24/60). Coverage must reach 100 % by the end frame.
- **SFX:** [ADD] `ember_stroke` (a sizzling marker stroke) `align='start'` at the draw-on, -6. `whoosh_fast` pass at the wipe's middle, -4. `impact_soft` at full cover, -8. Desi option: [ADD] `sitar_meend` up a 4th on the draw-on.
- **Grid:** the draw-on starts on a beat; full cover on the next beat.
- **Set rule:** a full Y5 wipe in **one** reel only; everywhere else the underline just underlines.

#### Y6 · Scramble-decode cut
- **Feel / when:** "cracking the algorithm", secrets revealed, tech-edge.
- **Timing:** 15-21 frames.
- **Ease:** `T.Glyphs(word, 'jw_mono', px=…).scramble(cv, t, x, y, t0, dur=0.7, stagger=0.04, rate=22)`. The scene swaps at 50 % decode under a 3-frame D7 RGB split.
- **Blur:** 3.
- **SFX:** `typing` (`params=dict(n=len(word), cps=16)`), -8, or `glitch_short` at the swap, -6. `ui_tick` on 16ths while resolving, -14. `check_ding` on the resolve, -8, pitched in key.
- **Grid:** the resolve on a beat.

### 3.5 LIGHT / FILM family (ref2's "light is the transition", in ember)

#### L1 · Light-leak burn (ember) ★
- **Feel / when:** warmth, memory, hope, golden nostalgia. The brand's most natural glue. 12-20 frames reads as punctuation; 24-36 frames as a dream.
- **Ease:** `sweep = K.ramp(t, c - d/2, c + d/2, 'linear')`. `K.light_leak` has a built-in sin(π·sweep) envelope that peaks at u = 0.5, which is the cut. Add an L3 push of 0.3-0.6 at c.
- **Blur:** 3 (a screen overlay needs no motion blur).
- **Build:** `K.light_leak(cv, t, colors=EMBERS, strength=1.2, seed=REEL_SEED, sweep=u, angle=35)` after the scene draw and before `finish()`. For an invisible cut the leak must cover **≥ 70 % of the frame at u = 0.5**. Check the luma coverage on frame c−1 in QA. Ref2 builds its version from `[C['EMBER'], C['FLAME']]` (`ref2_analysis.md` device 6).
- **SFX:** `reverse_swell(duration=d/2)` ending at c, -4, and `shimmer` at c, -8. The punchier version adds `flash_hit` -6. Music: a chord change on c, or a filtered riser into c.
- **Grid:** c on a downbeat or beat 3.

#### L2 · Film burn
- **Feel / when:** a memory dying, the end of a chapter, "jal gaya" (it burned). Vintage.
- **Timing:** 18-30 frames, with 2 white-hot frames, then B emerging from black.
- **Ease:** burn radius `in_cubic` to 60 %, then `in_expo` to full (the toolkit has no quad eases); B fades in from the centre over 6 frames `out_cubic`.
- **Blur:** 3.
- **Build:**
```python
X, Y = grid4(); n = up(fbm(11, scale=5))
d = up(np.hypot(X - x0, Y - y0) / K.H) + 0.35 * n            # noisy distance from the hot spot
m = np.clip((r(t) - d) / 0.01, 0, 1)                         # burned area
ring = np.exp(-((d - r(t)) / 0.012) ** 2)[..., None]
cv = A_t * (1 - m)[..., None]                                # burns to BLACK (multiplicative: blacks stay black)
cv[..., :3] += ring * (K.C['FLAME'] * 3.0 + np.float32([1.0, 0.85, 0.6]) * 2.0 * ring)   # white-hot core
# then B fades in from black inside m; finish(..., grain=0.035) for the frame's last 10 frames
```
- **SFX:** [ADD] `film_burn` with its hit at full burn, -3. Add `downlifter` -8 when it ends a chapter. Music: a memory filter (LP 900 Hz) or a drop-out.
- **Grid:** full burn on a downbeat.

#### L3 · Exposure-push flash frame (blacks never lift). Glue for every reel.
- **Feel / when:** a camera-flash memory, punctuation, a beat accent.
- **Timing:** 2-4 frames. It peaks on the cut frame and decays at 16/s (half-life ≈ 1.3 frames).
- **Build:** `finish(cv, t, LOOK, cuts=CUTS)`, i.e. `K.post(..., exposure=1.4*push, bloom=bloom*(1+0.9*push))`. **Never** use `K.flash`, `K.fade` or `post(flash=)`: they add an ivory term and lift the blacks into a grey veil (`recipes.md`). Ref2's analysis proposed a warm `flash=` bloom. Prefer the exposure push, which is multiplicative and keeps the kit's crushed blacks.
- **SFX:** `flash_hit` hit at c, 0 (its 0.1 s suck precedes it). For hero beats add `sub_drop` -6. The photo version uses `camera_shutter` -6.
- **Grid:** on a beat (montages: every beat or 8th). It is the default way to sell a hard cut.

#### L4 · Halation bloom-out wipe ★
- **Feel / when:** dreamlike transcendence, "sapne mein" (in a dream). Ref2's bloom blow-outs (0.77 s) without the white-out: the highlights flood into a **red-orange halation**, then resolve into the next world.
- **Timing:** 16-24 frames (8-12 out, 8-12 in).
- **Ease:** k = sin²(πu); the cut at u = 0.5.
- **Blur:** 3.
- **Build:** `finish(cv, t, LOOK, bloom=K.lerp(b0, 2.8, k), bloom_threshold=K.lerp(0.45, 0.12, k), halation=K.lerp(0.16, 0.9, k), exposure=0.6*k, vignette=K.lerp(0.45, 0.62, k))`. The blacks stay because the threshold stays above 0, halation only adds to highlights, the vignette grows and the kit crushes the toe. Compose A's last frames and B's first frames around a bright practical (window, monitor, lamp, sun) at about the same screen spot; this pairs with M2.
- **SFX:** `shimmer` -8, and `reverse_swell(duration=d/2)` ending at c, -6. Music: a soft reverse-cymbal swell from score.py. Intimate palette.
- **Grid:** c on beat 1.

#### L5 · Anamorphic lens-flare wipe
- **Feel / when:** sci-fi or premium-tech energy, a "launch". Ref2 ignites an anamorphic streak at 27 s that the type sits on (device 7).
- **Timing:** 10-16 frames.
- **Ease:** the flare source x(t) `inout_cubic` from −300 to 1380 px; intensity sin(πu).
- **Blur:** 5.
- **Build:** `fl = K.streak(2600, 90, K.C['FLAME']*3.0, K.C['AMBER']*4.0)` built once; `K.draw(cv, fl, x(t), y0, mode='add', opacity=I)` plus `finish(..., anamorphic=0.9*I, anamorphic_color=K.C['FLAME'])`. Swap the scene behind the 300-px saturated core band: a soft vertical mask following x(t), feather 120 px.
- **SFX:** `whoosh_fast` pass at c, -4. `shimmer` -8. `sparkle` -12.
- **Grid:** the core crosses the centre on a beat.

#### L6 · Projector / film-gate slip
- **Feel / when:** flashback, "bachpan" (childhood), archive, an editor's love of film.
- **Timing:** a 6-10 frame slip, then 1 bar of 24 fps judder.
- **Ease:** step functions. Film cadence: evaluate the scene at `floor(t*24)/24`. The slip moves one frame-height down over 6 frames, with a 60 px black frame line crossing.
- **Blur:** 1-3 (no blur during the judder: it must stutter like film).
- **Build:** a film-frame overlay of **our own** design (`ui.Surf` sprocket holes, edge text `JAWAD · EMBER 800T · 24`). Never copy ref3's "KODAK PORTRA 400" or its white-paper frame. Flicker: a multiplicative exposure of ±0.08 stops at 12 Hz (never additive). Gate weave: `K.wiggle(t, 6, 1.5)` px. Grain 0.035. Vertical scratches: alpha 0.1 at a random x per 24 fps frame.
- **SFX:** an [ADD] `projector_rattle` bed (24 Hz sprocket clicks plus motor) for the length of the flashback, -18. `camera_shutter` on the slip, -8. Music: memory filter during the flashback (LP 900 Hz, mono, -6 dB). Desi: a harmonium drone.
- **Grid:** the slip on a downbeat; a flashback lasts 2 or 4 bars.

#### L7 · Light-beam (god-ray) sweep ★
- **Feel / when:** the aha moment, hope cutting through darkness ("andhere mein roshni", light in the dark). The volumetric vocabulary of ref2 and ref3, in ember.
- **Timing:** 18-30 frames.
- **Ease:** beam angle or position `inout_sine`; intensity sin(πu)·1.2.
- **Blur:** 3-5.
- **Build:** a soft emissive beam: `K.draw_quad(cv, beam_spr, quad(t), mode='add')`, with `beam_spr = K.streak(...)` stretched into a trapezoid from a source above the frame. Then `K.god_rays(cv, center=src_xy, strength=0.6*I, threshold=0.4, length=0.5, tint=K.C['AMBER'])`. Swap the scene under the beam core (mask = beam alpha > 0.6, widened 80 px). Dust in the light: multiply the `J.embers(...)` brightness by the beam mask.
- **SFX:** `whoosh_slow` pass, -6. `shimmer` -8. Under it, a choir-like pad swell or a [ADD] `harmonium_swell` (desi).
- **Grid:** the beam crosses the centre on a downbeat.

#### L8 · Aperture iris close/open
- **Feel / when:** camera POV, "the take", a chapter end. The editor's camera world.
- **Timing:** close 8 frames (`in_cubic`), 2 frames of black, open 10 frames (`out_back`, s = 1.2).
- **Blur:** 3.
- **Build:** a 7-blade iris: a heptagon of radius r(t) rotated θ(t) = 0 → 25°, masked with `ui.fill_mask`. The blade edges are rim-lit with FLAME (`ui.stroke_mask` + glow).
- **SFX:** `camera_shutter` hit at the close, 0. `ui_click` at the open start, -8. `reverse_swell(duration=0.3)` into the open, -8.
- **Grid:** the black frames centre on a beat.

### 3.6 DIGITAL / EDITOR-NATIVE family (Jawad's unfair advantage)

UI rules:
- **Generic NLE design only:** no Adobe, CapCut or DaVinci logos, icons or trade dress. Use the `ui` look `'ember'` (smoky warm-black glass, FLAME rim, RED hot spot) and `jw_mono` readouts.
- UI text ≥ 34 px after perspective.
- Pure scene functions make time tricks (scrub, rewind, ramp) free: you only ask the scene for another t.

#### D1 · Timeline playhead scrub ✂
- **Feel / when:** the editor's superpower. Fast-forward or rewind through a life or story, a time-skip, the meta reveal "ye sab edit tha" (this was all an edit). It is a strong share trigger ("tag your editor").
- **Timing:** 36-60 frames: pull back into the UI over 10 frames (`out_expo`), scrub for 16-30 frames, push back in over 10 frames (`in_expo`).
- **Ease:** the playhead `x(t)` is a `K.Track` with `inout_expo` (the scrub), then lands on a marker with the SNAP spring (3.0, 0.55).
- **Blur:** 5 during the pull and push. During the scrub use 3, and update the monitor at **12 Hz** (real scrubbing stutters).
- **Build:**
```python
win = ui.app_window(w=980, h=1500, look='ember', title='reel_v07_FINAL_final2.mp4', header='', sidebar=False)
def monitor(t):                                    # the reel's own earlier scenes at the scrubbed source time
    src = SCRUB(t)                                 # K.Track of SOURCE seconds, e.g. 4.0 -> 19.0 -> 11.2
    return REEL_SCENE(math.floor(src * 12) / 12)   # quantised to 12 Hz updates
# face = win.face_at(sweep=(t*.35) % 1); lanes: ui.Surf rrects (V1 FLAME clips, V2 EMBER, A1 waveform drawn
# from the real VO stem envelope); playhead: a 3 px RED line + handle, K.glow; timecode in 'jw_mono' (>= 34 px).
# Camera: the monitor slot fills 1080x1920 exactly at the start/end frames (solve the distance as in M4);
# mid-scrub the window tilts rot=(6, -10, 0) at dist*1.6.
```
- **SFX:** [ADD] `scrub`: a granular re-read of **the reel's own mix** between the source times. The pitch follows the playhead speed and runs reversed when the playhead goes backwards. -6. `ui_tick` on each clip-boundary crossing, -12. `ui_click` on the stop, 0. Music: drops out during the scrub (the scrub *is* the music) and returns on the downbeat with `impact_soft`.
- **Grid:** the pull-back starts on a beat; the stop lands on a downbeat.

#### D2 · Razor-tool cut ✂
- **Feel / when:** a decisive break ("purana Jawad | naya Jawad", the old Jawad | the new Jawad), cutting the past. Comedy: "client ka feedback → cut" (the client's feedback → cut).
- **Timing:** cursor approach 6-10 frames, click 1 frame, split and slide 8-12 frames.
- **Ease:** the halves separate `out_expo` 0 → 60 px and rotate ±2°, then fly off `in_expo` (or stay, with B behind).
- **Blur:** 5 on the separation.
- **Build:** an [ADD] razor cursor icon. An SVG path goes through `ui.parse_path` → `ui.fill_mask`, filled IVORY with a FLAME glow (`ui.draw_cursor` has only 'arrow' and 'hand'). At the click, draw a full-height 3 px emissive FLAME line at x_c (`K.glow`). A splits into two sprites at x_c, each drawn as a plane with a small tilt and `ui` shadow, with B behind. The vertical line is the NLE metaphor. For 9:16 composition a horizontal blade is also fine.
- **SFX:** [ADD] `razor_snip` hit at the click, 0. `card_slide` -8 as the halves move. The music is **gated exactly at the click for ½ beat**: the razor "cuts" the music too. B's music enters on the next beat.
- **Grid:** the click on beat 4; B on the next downbeat.

#### D3 · Render-progress-bar wipe ✂
- **Feel / when:** before → after (raw/log versus graded), patience → payoff ("jab render complete hota hai", when the render completes). Jawad's craft, shown.
- **Timing:** 30-60 frames of irregular progress, then an 8-frame flourish.
- **Ease:** progress `p(t) = K.Track([(t0, 0.0, 'out_cubic'), (t0+.35, .22, 'hold'), (t0+.55, .22, 'inout_cubic'), (t0+1.0, .64, 'hold'), (t0+1.15, .64, 'out_expo'), (t0+1.6, 1.0)])`. That is a realistic stall, then a fast last third. The wipe edge is `p·H`, rising from the bottom, which suits 9:16.
- **Blur:** 3.
- **Build:** A is a "log/raw" version of B: luma compressed toward a 0.35 grey, desaturated 70 %, no bloom. B is the graded `ember` version of the same frame. `m = Y > (1 - p) * H` with a 24 px feather, plus a 2 px emissive FLAME edge line. The progress pill is a `ui.Surf` rrect, with "Rendering… 63%" in `'jw_mono'` (an integer % from p). At 100 %: `ui.toast('Export complete', look='ember')`, or Roman Urdu "Ho gaya" (done).
- **SFX:** `bar_grow` `align='start'` with `params=dict(duration=fill_len)`, -8. `ui_tick` on each resume after a stall, -14. At 100 %: `toast_chime` -4 (pitch in key) and `impact_soft` -6. Music: a riser ending on 100 %, then the drop.
- **Grid:** 100 % = a downbeat.

#### D4 · Keyframe-graph swoosh ✂
- **Feel / when:** "smooth" is a craft; this shows the invisible work (easing). The editor's flex, between the "rough" and "smooth" versions of a move.
- **Timing:** graph draw-on 10 frames, then the dot's travel 14-20 frames.
- **Ease:** **single source of truth:** `EASE_SHOW = K.bezier(0.7, 0.0, 0.2, 1.0)` is both drawn as the curve and used for the camera move.
- **Blur:** 5-7 during the move.
- **Build:** a graph panel (`ui.glass_card(820, 560, look='ember')`, grid lines, the curve sampled from `EASE_SHOW` as a value graph or as its derivative for a speed graph). Bezier handles are small diamonds + handle lines (`ui.Surf`). The keyframe diamonds pop with POP (2.6, 0.5). A glowing dot rides the curve. At the steep section the background whips (C1) in sync: the steepest point is the cut. Note: AE speed graphs are not plain cubic beziers ([Adobe forum, the math of speed graphs](https://community.adobe.com/t5/after-effects-discussions/what-s-the-math-behind-speed-graphs/m-p/9597181)), so draw the **value** graph, which is the true bezier.
- **SFX:** [ADD] `keyframe_pop` (= `pop` pitch 1.2, -8, plus `ui_tick` -14) per diamond. `swish_small` along the curve with `rate` scaled by the dot's speed, -10. `whip` at the steepest point (the cut), -4.
- **Grid:** keyframes pop on 8ths; the steepest point lands on a beat.

#### D5 · UI window swap (SaaS)
- **Feel / when:** smoothness, productivity, a workflow story. Processes with several steps ("hook → story → edit → sound").
- **Timing:** 12-18 frames with a 4-frame overlap.
- **Ease:**
  - A exits over 10 frames, `in_cubic`: z +0 → +600, rot_y 0 → −28°, opacity 1 → 0.
  - B enters over 14 frames with POP (2.6, 0.55): x +900 → 0, rot_y 24° → 0.
- **Blur:** 5.
- **Build:** `win.plane(cv, cam, center, width, rot=..., face=win.face_at(sweep=...))` for both windows. A comet rim runs on B as it lands. Text goes into `win.meta['slot']` only.
- **SFX:** `whoosh_fast` pass, -6. `card_slide` (the thup on landing), 0. `glass_tap` on the settle, -10, pitched in key.
- **Grid:** the landing on a beat.

#### D6 · Glitch / datamosh-lite
- **Feel / when:** system crash, overwhelm, "algorithm" chaos, breaking a pattern. Edgy. **Once per reel, 0.4 s maximum.**
- **Timing:** 6-12 frames.
- **Ease:** stepped: hold each displacement 2 frames.
- **Blur:** 1.
- **Build:** [ADD] P-frame bleed. Take the Farnebäck optical flow of A's last 6 frames at ¼ res (`cv2.calcOpticalFlowFarneback`, cached per frame index). Push **B's** first frame through the accumulated flow (`cv2.remap`), block-quantised to 16 px. Add random row shifts (±40 px) and D7's channel offset. Datamosh mechanics: deleted or delayed I-frames make old motion move new pixels ([Adobe explainer](https://adobe.com/uk/express/learn/blog/what-is-datamosh)).
- **SFX:** `glitch_short` hit at the onset, 0. [ADD] `data_crunch`: a 6-bit / 8 kHz bit-crush of the mix at that moment, -6. Music: a stutter-gate (repeat a 1/16 slice ×4).
- **Grid:** starts on the "and"; resolves on the beat.

#### D7 · RGB-split chroma shock
- **Feel / when:** impact, adrenaline. Pairs with Y3 slams; a CapCut 2026 staple ([CapCut](https://www.capcut.com/help/capcut-transitions)).
- **Timing:** 2-4 frames.
- **Ease:** `imp = K.impulse(t, c, decay=20)`.
- **Blur:** 3.
- **Build:** `finish(..., chroma=1.4 + 14*imp)` (radial). Add [ADD] a linear channel offset on RGB only (premultiplied-safe): shift R by +k px and B by −k px horizontally, k = 18·imp, then scale the frame 1.03 → 1.0.
- **SFX:** `glitch_short` -6 + `whip` -8, or `impact_soft`.
- **Grid:** on a beat or an 8th.

#### D8 · Speed-ramp (velocity) cut
- **Feel / when:** hype, flow, the "velocity edit" culture. CapCut ranks velocity edits among the biggest trending transitions of 2026 ([CapCut](https://www.capcut.com/help/capcut-transitions)).
- **Timing:** 10-16 frames around the cut: A ramps up over 6-8 frames, B ramps down over 6-8 frames.
- **Ease:** scene-time speed: A goes 1× → 6× (`in_expo`), B goes 6× → 1× (`out_expo`). Integrate the speed so scene time stays continuous.
- **Blur:** 7 near c (fast scene time gives strong real motion blur).
- **Build:**
```python
def warp(t, c, w=0.25, peak=6.0, n=96):
    """Scene time with a speed bump centred on c: speed 1 -> peak (in_expo) -> 1 (out_expo). Continuous; pure."""
    if t <= c - w:
        return t
    ts = np.linspace(c - w, min(t, c + w), n)
    u = (ts - (c - w)) / w                                     # 0..2 across the window
    sp = 1 + (peak - 1) * np.array([K.EASE['in_expo'](x) if x < 1 else 1 - K.EASE['out_expo'](x - 1) for x in u])
    return t + float(np.trapz(sp - 1, ts))                     # after c + w the extra time stays constant
# A(warp(t, c)) before the cut, B(warp(t, c) - offsetB) after it. Footage: F.SpeedRamp([...]) on the clip.
```
- **SFX:** `whoosh_fast` pass at c, -4. `riser(duration=0.35)` ending at c, -8. `impact_soft` at c, 0. Music: on the beat.
- **Grid:** c on a beat.

#### D9 · Undo / Ctrl+Z rewind ✂
- **Feel / when:** a second chance ("ek galti... Ctrl+Z", one mistake... Ctrl+Z), regret → redo. Comedy or emotion. It pairs with the History-panel idea in `hooks_retention_captions.md`.
- **Timing:** key-press toast 6 frames, rewind 18-30 frames, snap 2 frames.
- **Ease:** rewind time `τ(t) = t_press − R·in_cubic(u)` (accelerating backwards), then a hard stop at the restore point with an L3 push.
- **Blur:** 5 (backwards motion blur looks right).
- **Build:** keycaps `ui.chip('Ctrl', look='ember')` + `ui.chip('Z', ...)` with press impulses. A small history panel (a glass list) highlights steps backwards. The scene is evaluated at τ(t), so the rewind costs nothing extra. During the rewind add desaturation 30 % and `K.zoom_blur(0.02)`. **No VHS clichés.**
- **SFX:** `typing` (`params=dict(n=2, cps=8)`) for Ctrl and Z, -6. [ADD] `tape_rewind`: a reverse-granular re-read of the mix at −2× to −8× with LP, -6. `impact_soft` on the restore. Music: score.py **tape-stops** the music at the press (pitch → 0 over 0.4 s), stays silent through the rewind, and on the restore **restarts the score from the earlier bar** (`score.restart_at(bar)`). The music literally undoes too.
- **Grid:** the press on beat 4; the restore on a downbeat.

### 3.7 ORGANIC family

Organic recipes live at ¼ res: noise from `fbm()`, masks upsampled, colour from palette tokens.

#### O1 · Ink bleed (deep red ink)
- **Feel / when:** grief, heaviness, slow realisation, poetry ("dil pe daag", a stain on the heart).
- **Timing:** 30-45 frames.
- **Ease:** radius `out_cubic` with domain-warped noise.
- **Blur:** 3.
- **Build:** `d = dist(x, p0)/H + 0.25*fbm(7)` (warped by a slow offset), `m = smoothstep(r(t), r(t) - 0.05, d)`. B is revealed through the ink. The edge band *darkens* A subtractively: multiply by `K.C['EMBER']*0.25` (ink darkens, it never glows). Add a watercolour edge ring 1.3× darker.
- **SFX:** [ADD] `ink_bloom` at the drop, -4. `whoosh_slow` -10. Music: a single felt-piano note + pad. Intimate.
- **Grid:** the drop on a downbeat; the bloom completes over 1-2 bars.

#### O2 · Smoke wipe
- **Feel / when:** mystery, passing through confusion ("dhuan", smoke), aftermath.
- **Timing:** 24-36 frames.
- **Ease:** the threshold follows `inout_sine`.
- **Blur:** 3.
- **Build:** smoke density = `fbm` advected upward (y offset −v·t) with domain warp, lit by a FLAME rim from below (density gradient · light direction). Mask = density > threshold(t). B is revealed as the smoke clears.
- **SFX:** `whoosh_slow` -6. A `night_air` bed swell (bed list: `gain_db` +6 over 2 s). `impact_soft` -10 as it clears.
- **Grid:** the clear on a downbeat.

#### O3 · Page tear (black paper; not ref3's white paper)
- **Feel / when:** "naya chapter" (a new chapter), rejecting the old script, an editorial rebel.
- **Timing:** 12-20 frames.
- **Ease:** the tear progresses along a jagged path `in_cubic`. The torn half lifts (rx 0 → 35°, rz −8°) and flies off `out_expo`.
- **Blur:** 5.
- **Build:** A on a black-paper texture. The tear path is a polyline with noise. The fibrous edge is an IVORY fibre mask (`ui.stroke_mask` with a noisy 2-6 px width). The top part is drawn with `K.draw_plane` (rotation + shadow), with B underneath.
- **SFX:** [ADD] `paper_tear` `align='start'`, 0. `card_slide` on the fly-off, -10.
- **Grid:** the tear ends on a beat.

#### O4 · Shatter (glass)
- **Feel / when:** breaking a limit or belief ("ye soch tod do", break this way of thinking). An explosive reveal.
- **Timing:** 15-24 frames, with an optional 10-frame 0.25× slow-mo in the middle (D8 time-warp).
- **Ease:** ballistic: shard velocity outward and toward the camera, with spin and slight gravity. The impact frame gets an L3 push.
- **Blur:** 7-9 (shards cross the near plane).
- **Build:** Voronoi shards (`scipy.spatial.Voronoi` on 40-70 seeds, denser near the impact point). At c, crop A by each polygon into a sprite (built once). Draw each shard with `K.draw_plane` using its own `rot(t)` and `z(t)`; near-plane clipping handles shards that fly through the lens. Edges get a thin AMBER specular rim. B is behind.
- **SFX:** [ADD] `glass_shatter` hit at c, 0. `sub_drop` -4. Epic: `impact_big` -6. A tinkle tail. Music: the drop on c.
- **Grid:** c on a downbeat.

#### O5 · Molten pour (ember liquid)
- **Feel / when:** "tapa ke sona bana" (heated until it became gold), craft forged in heat. Pure brand energy.
- **Timing:** 24-36 frames.
- **Ease:** the front's y(t) `in_cubic`; cooling is an exponential decay of emission over 12 frames.
- **Blur:** 3-5.
- **Build:** the liquid front is a metaball field (a sum of moving Gaussians) thresholded with a soft edge. Inside: an emissive core `K.C['FLAME']*3 → K.C['AMBER']*5` at thin parts, and a dark `fbm` crust. After full cover the emission decays to EMBER, then black. B is revealed by glowing cracks (a Voronoi edge mask) that widen.
- **SFX:** [ADD] `molten_pour` `align='start'`, 0. `bubble_pop` grains at -14 (`rate` 0.6). `impact_soft` at full cover, -6. Music: a low [ADD] `braam` at -6.
- **Grid:** full cover on a downbeat.

#### O6 · Ember disintegration ★
- **Feel / when:** letting go and rebirth ("purana main raakh, naya main aag": the old me is ash, the new me is fire). The most on-brand transition: FLAME and RED embers on black. Ref2 ends on a disintegration (`ref2_analysis.md` device 15); ours is fire, not liquid glass.
- **Timing:** 30-45 frames.
- **Ease:** an erosion front sweeps across the frame `inout_sine` (or radially from a point). The particles decelerate and cool from white-hot → FLAME → RED → EMBER → dark over 1.2 s.
- **Blur:** 3-5.
- **Build:** [ADD].
  - At c0, sample N = 6000 points from A's luminance (weighted) once.
  - Erosion mask: `m = smoothstep(front(t) - (x + 120*fbm))`. A stays visible where it is not eroded.
  - The 20-px edge band is emissive FLAME.
  - Each particle spawns at its pixel when the front passes it, then advects with `p = p0 + v·τ + K.wiggle` and rises at −46 px/s (the `J.embers` velocity).
  - Draw the particles additively into a ½-res buffer with `np.add.at`, then add a `gblur` σ 1.5 glow.
  - B is behind, or B rises from black after a drop-out.
- **SFX:** [ADD] `ember_crackle` `align='start'` for the erosion length, -4. `whoosh_slow` -8. On completion: the **drop-out** (½ beat of silence), then `impact_big` on B's reveal. This is the classic silence → hit (§4.4).
- **Grid:** starts on a beat; completes one bar later; B is revealed on the next downbeat.

---------------------------------------------------------------------------------------------------------------

## 4. Sound design for cinematic storytelling

Nobody on the team can listen, so every rule here can be checked with numbers (Section 4.9). The SFX engine is `audio.py`: SFX only, pre-balanced, `align='hit'`. New sounds come from [ADD] `jawad_sfx.py` (§4.8), registered into `audio.SOUNDS` at runtime and owned by the sound-designer. Music lives in `score.py` (§5.4), so `audio.py` stays SFX-only.

**Density targets.**
- Ref2 runs about 0.85 designed SFX events per second (14 sub impacts + 16 air risers in 35 s), and **every world change gets a sub hit within ±0.15 s** (`ref2_analysis.md` §audio).
- Ref1 is music-dense, at about 5 onsets per second.
- For VO-led reels the target is **0.6-1.0 designed events per second (20-35 cues in 35 s)**: a sub-weight hit on every world change, a riser or reverse swell ending on every light event, and at most 3 caption SFX per reel (`hooks_retention_captions.md` caption rules).
- Sound design is what makes a cut feel intentional and lifts perceived quality on a noisy feed, and the reel must also work muted ([IRPR Sound guide](https://sounddesign.irpr.agency/guides/how-sound-design-improves-reels/)).

### 4.1 Mix architecture: VO first

| stem | made by | level before the final sum | notes |
|---|---|---|---|
| **VO** (Hinglish TTS, Hindi male voice) | hinglish-scriptwriter TTS → `vo_chain()` below | **-16 LUFS integrated**, peaks ≤ -3 dBTP | ref2's VO F0 median is 117 Hz (male), and a Hindi TTS male voice sits at about 100-150 Hz |
| **SFX + bed** | sound-designer `<module>_sfx.py` → `A.mix(...)` | **-18 LUFS** (audio.py default), TP ≤ -2.0 | detail cues inside VO windows -4 to -8 dB (helper below) |
| **Music** | `score.py` (§5.4) or a licensed track | -18 LUFS when there is VO, -16 without | frequency-ducked under VO in score.py, then broadband-ducked by music-supervisor |
| **Final** | music-supervisor final mix | **-14 LUFS ±0.5**, TP ≤ -2.0 dBTP (wav), ≤ -1.5 after AAC, LRA 5-9 LU | speech ≥ 8 LU above music (median over voiced frames) |

- Instagram publishes no official loudness spec. Third-party guides converge on about **-14 LUFS / -1 dBTP** for Reels, and some argue for -16 for dialogue-led pieces ([OpenClip LUFS guide](https://openclip.app/learn/lufs.md); [dialogue loudness, Joseph Nilo](https://josephnilo.com/blog/dialogue-loudness-lufs-true-peak-video/)).
- Ref1 masters at -14.2 LUFS but with true-peak overs (+0.3 dBTP). We keep -14 with a stricter **-2.0 dBTP** wav ceiling for AAC headroom, and **-16 for the VO stem**: the VO is the anchor and everything else is ducked around it.

**VO chain** (`vo_chain`, run once on the TTS wav before the final mix. All of these are audio.py DSP calls):
```python
import numpy as np, audio as A
def vo_chain(x):
    x = A._st(A.hp(x, 80, 2))                                   # rumble / TTS DC
    x = A.eq(x, 'peak', 280, q=1.0, gain_db=-2.0)               # de-mud (male chest)
    x = A.eq(x, 'peak', 3000, q=1.0, gain_db=+2.0)              # presence: intelligibility on phone speakers
    x = A.eq(x, 'hs', 10000, q=0.7, gain_db=+1.5)               # air
    s = A.bp(x, 5500, 9000)                                     # de-ess: compress only the sibilant band
    gs = A.compressor_gain(s, thresh_db=-30, ratio=4.0, knee_db=4, attack=0.002, release=0.06)
    x = x - s + s * A.undb(gs)[:, None]
    g = A.compressor_gain(x, thresh_db=-22, ratio=3.0, knee_db=6, attack=0.008, release=0.12)
    x = x * A.undb(g)[:, None]                                  # 3:1, about 3-5 dB GR on stressed words
    x = A.reverb(x, 'room', wet_db=-26)                         # glue: almost dry, close-mic intimacy
    return x * A.undb(-16.0 - A.loudness(x))
```
Breaths: TTS often has none. Before emotional lines, an [ADD] `breath_in` ending at the first syllable (-14) makes the voice human. It is an intimate pre-lap.

**SFX under the VO (cue-level ducking and carving).** `A.mix()` has no VO input, so the cue sheet does it. Word times come from faster-whisper on the TTS track (Devanagari), as the captions pipeline already does.
```python
AIR  = {'shimmer', 'sparkle', 'ripple', 'swish_small', 'ui_tick', 'ui_hover'}            # keep only > 5 kHz
DARK = {'whoosh_fast', 'whoosh_slow', 'whoosh_by', 'impact_soft', 'sub_drop', 'card_slide', 'heartbeat', 'air_zoom'}
MID  = {'glass_tap', 'check_ding', 'toast_chime', 'ui_click', 'typing', 'pop', 'camera_shutter', 'whip', 'riser'}
HERO = {'impact_big', 'flash_hit', 'logo_sting', 'braam', 'glass_shatter'}                # must sit in VO gaps
def vo_windows(words, pad=0.06):                     # [{'start', 'end'}] -> merged [(t0, t1)] speech windows
    out = []
    for w in sorted(words, key=lambda w: w['start']):
        a, b = w['start'] - pad, w['end'] + pad
        if out and a <= out[-1][1] + 0.12: out[-1] = (out[-1][0], max(out[-1][1], b))
        else: out.append((a, b))
    return out
def fit_under_vo(cues, wins, depth=-6.0):
    for c in cues:
        hit = c['t']                                          # align='hit' cue time = the designed hit
        if not any(a <= hit <= b for a, b in wins): continue
        if c['name'] in HERO: raise ValueError(f"hero cue {c['name']} at {hit:.2f}s lands on a word: move the transition into a VO gap")
        c['gain_db'] = c.get('gain_db', 0) + depth
        if c['name'] in AIR:  c.setdefault('hp', 5500)
        if c['name'] in DARK: c.setdefault('lp', 1100)
        if c['name'] in MID:  c['gain_db'] -= 2.0             # mid-band sounds compete with consonants: extra -2
    return cues
```
- Hero hits sit in VO gaps: at least 120 ms clear before a transient and 300 ms after it for `impact_big`. Ref2's transitions follow a phrase end by 0.03-0.65 s (median about 0.3 s).
- Music under the VO uses frequency ducking plus a broadband duck: about -10 dB in the speech band and -6 dB elsewhere (§5.4 `mixdown`). This combines the practice of notching the music where the voice lives, then ducking ([Adobe Audition community tutorial](https://community.adobe.com/questions-544/tutorial-better-automated-ducking-for-music-behind-voice-overs-158467); [IRPR: ducking vs EQ separation](https://sounddesign.irpr.agency/compare/ducking-vs-eq-separation/)).

### 4.2 Hit layering: transient + body + sub + tail

Trailer practice: a hit is a **sharp transient + a mid "body" + a felt sub + a long reverb tail**. All the layers trigger together; the low end is cleaned from all but the sub layer; saturation helps the hit cut through; and impacts depend on contrast and silence before them ([Ableton, high-impact sounds for trailers](https://www.ableton.com/de/blog/learn-how-to-make-high-impact-sounds-for-movies-and-trailers/); [Morphic, layering](https://morphic.com/resources/how-to/how-to-layer-sound-effects); [Violet Recording, trailer sound design](https://violetrecording.com/sound-design-for-trailers/)).

| layer | band | life | catalog source | offset | gain |
|---|---|---|---|---|---|
| transient | 2-9 kHz | 0-15 ms | `flash_hit` (crack), `ui_click`, `camera_shutter`, [ADD] `razor_snip`, [ADD] `tabla_na` | **−3 ms** (it leads) | -3 to -6 |
| body | 120 Hz-2 kHz | 15-250 ms | `impact_big`, `impact_soft`, `card_slide`, [ADD] `tabla_dha`, [ADD] `dholak_ghe` | 0 | 0 |
| sub | 30-90 Hz | 0-1.6 s | `sub_drop` (has phone harmonics), the score's 808 | 0 | -3 to -6, `lp: 120` |
| tail | broadband | 0.3-4 s | `impact_big`'s hall, `logo_sting` air, room send, `shimmer`, [ADD] `ghungroo` | 0 to +50 ms | -8 to -12 |

The four house stacks (cue lists for `<module>_sfx.py`; `B()` and `BPM` from the reel module):
```python
def ember_slam(t0, riser_beats=4, gap_beats=0.0):          # EPIC hero reveal / title slam
    r_end = t0 - gap_beats * 60.0 / BPM                      # gap > 0 = the drop-out (4.4)
    return [dict(t=r_end, name='riser', params=dict(duration=riser_beats * 60.0 / BPM), gain_db=-4),
            dict(t=t0 - 0.003, name='flash_hit', gain_db=-3),                       # transient leads by 3 ms
            dict(t=t0, name='impact_big', gain_db=0),                                # body + hall tail
            dict(t=t0, name='sub_drop', gain_db=-4, lp=120, params=dict(dur=1.6))]   # sub
def velvet_hit(t0, pitch=1.0):                               # INTIMATE: a heartbeat-sized landing
    return [dict(t=t0, name='heartbeat', params=dict(n=1), gain_db=-6),
            dict(t=t0, name='impact_soft', gain_db=0),
            dict(t=t0 + 0.02, name='glass_tap', params=dict(pitch=pitch), gain_db=-10)]  # tonal tail in key
def glass_truth(t0, pitch=1.0):                              # TECH / UI reveal
    return [dict(t=t0 - 0.002, name='ui_click', gain_db=-6),
            dict(t=t0, name='glass_tap', params=dict(pitch=pitch), gain_db=0),
            dict(t=t0, name='sub_drop', params=dict(dur=0.8), gain_db=-10, lp=120),
            dict(t=t0 + 0.03, name='sparkle', gain_db=-10)]
def dha_hit(t0, sa_hz):                                      # DESI reveal ([ADD] sounds, 4.8)
    return [dict(t=t0, name='tabla_roll', params=dict(n=8, bpm=BPM, sa=sa_hz), gain_db=-6),   # ENDS on t0
            dict(t=t0, name='tabla_dha', params=dict(sa=sa_hz), gain_db=0),
            dict(t=t0, name='sub_drop', gain_db=-6, lp=120),
            dict(t=t0 + 0.05, name='ghungroo', gain_db=-12)]
```
- At most 3 sounds **start** on one instant; a riser or reverse swell that *ends* there does not count. `A.duck_under` trims clusters automatically: one equal neighbour gets -2.3 dB, three get -4.5 dB.
- **Tune tonal SFX into the key.** Measure each sound's dominant partial once and move it to the nearest octave of a chord tone:
```python
def f0_of(name, **p):
    x = np.asarray(A.sound(name, **p), float).mean(1); X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1 / A.SR); return float(f[np.argmax(X * (f > 150))])
def pitch_to(name, target_hz):                               # multiplier for params pitch= (or cue 'rate')
    r = target_hz / f0_of(name); return r * 2.0 ** -round(math.log2(r))
```
  This applies to `glass_tap`, `check_ding`, `toast_chime`, `ui_click`, `pop` and `coin_ring` (pitch param), and to `logo_sting` (`tone`). Other sounds take the cue `rate`, which changes speed and pitch together: use it only on tonal tails.

### 4.3 Pre-lap, J-cuts, L-cuts and sound bridges (frames at 30 fps)

A **sound bridge** is audio that carries across an edit. A **J-cut** lets the incoming audio start before the picture changes (sound leads). An **L-cut** lets the outgoing audio continue over the new picture ([Filmdaft, sound bridges](https://filmdaft.com/what-is-a-sound-bridge-in-film-definition-and-transition-guide/); [SpotlightFX, J and L cuts](https://spotlightfx.com/blog/what-are-j-cuts-and-l-cuts-professional-dialogue-editing-explained); [Wikipedia: J cut](https://en.wikipedia.org/wiki/J_cut)).

| device | rule | numbers |
|---|---|---|
| **VO pre-lap (J-cut)** | the next line starts before the picture cut: the voice pulls the viewer through the cut and there is no dead air | **4-9 frames (0.13-0.30 s)**; ref2 measured 0.29 s; the hooks research recommends 0.2-0.3 s |
| **world pre-lap** | the next world's ambience or bed fades in before its picture | ½ beat (10 f at 90 BPM) via a bed-list `fade`; for a flashback, the projector rattle leads by 1 beat |
| **transition pre-lap** | risers, reverse swells and whooshes are pre-laps by design (`align='hit'` ends or peaks on the cut) | the riser *starts* 1-4 beats before |
| **L-cut tails** | never cut a hit's tail at a picture cut: tails ring 0.5-2 s into the next shot | do not truncate with `dur` at the cut; limit only the final cue |
| **VO post-lap** | the old line finishes over the first frames of a reaction shot or insert | 4-10 frames |
| **sound bridge** | one sustained element runs unbroken across a montage so it reads as one thought | tanpura drone, harmonium note, room tone, a ticking pulse, the score's pad |
| **hook pre-lap** | frame 0 is already sounding: a hit or a word in motion, never a fade-in. The VO starts by 0.3 s (brand skill) | first cue at f0-f2; `hooks_retention_captions.md` "sound before picture": an editor sound on f0, explained at f6 |
| **on-word cut** | a hard cut on the stressed syllable of a one-word line | cut at the word's start time − 1 frame (the consonant onset) |

### 4.4 Silence as a weapon: the drop-out before the reveal

- **Why it works:** in Salimpoor et al. (2011), dopamine is released during the *anticipation* of a musical peak (caudate) and separately at the peak (nucleus accumbens). Withholding sound for a moment feeds the anticipation phase ([Nature Neuroscience 14:257-262, summary at BRAMS](https://brams.org/2011/01/09/salimpoor/); [Scientific American blog](https://blogs.scientificamerican.com/scicurious-brain/repost-this-is-your-brain-on-music/)). Trailer practice says the same: hits need contrast, so leave space and silence before them ([Violet Recording](https://violetrecording.com/sound-design-for-trailers/)).
- **Length:** ½-1 beat. That is 12-24 f at 75 BPM, 10-20 f at 90, 9-18 f at 100, and 12-24 f in 150's half-time. **True digital silence for at most about 8 frames.** Beyond that, keep **one** held-breath element alive: a breath, `heartbeat(n=1)`, a single clock tick, or room tone at about -45 LUFS. Feed silence longer than about 1 s makes people think the audio broke.
- **How it starts:** the riser or reverse swell **stops dead** at the drop-out start (the "suck"), or the music **tape-stops** (score.py `tape_stop`), or the razor (D2) gates it.
- **Picture during the silence:** it holds its breath too: a near-freeze (a 1 %/s push) or a silent type reveal (muted viewers still get it).
- **How it ends:** the **loudest moment of the reel**. A hit stack (`ember_slam` / `dha_hit`) plus the music's first full bar. QA: `max_momentary_lufs` of the reel falls within ±0.2 s of this hit.
- **Budget:** one drop-out per reel (the reveal), plus optionally the mid-reel re-hook (0.3-0.5 s of VO silence at 45-50 % of the runtime, `hooks_retention_captions.md` §re-hook). Ref2 has its dip at 16-17 s of 35 s, which is that re-hook.
- **Implementation:**
  - In score.py, `gate(t0, t1, fade=0.004)` is applied on the music **after** the reverbs.
  - SFX bed: a bed-list window with `gain_db: -60` and `fade: 0.004`.
  - Any SFX tail crossing the gap is cut with the cue `dur`, except the riser, which must end exactly at t0.

### 4.5 Risers into reveals

| role | length | layers | ends |
|---|---|---|---|
| small accent | 1 beat | `reverse_swell(duration=1 beat)` | on the hit |
| section change | 2 beats | `riser(duration=2 beats)` + score filter opening (LP 400 → 6 kHz) | on the hit |
| hero reveal | 4 beats (at 75 BPM: 2 beats + a Shepard bed) | `riser` + `reverse_swell` (last beat) + score roll (snare or **tabla tirakita**: 4ths → 8ths → 16ths → 32nds) + [ADD] `shepard_riser` for anything over 2.5 s | on the hit, or at the drop-out start |

- The Shepard tone (stacked octave sines gliding with a fixed spectral envelope) gives "endless" rising tension. Zimmer and Nolan use it across *Dunkirk*, *Interstellar* and the *Dark Knight* scores ([CBC: Hans Zimmer on Dunkirk](https://www.cbc.ca/radio/q/blog/hans-zimmer-explains-the-audio-trickery-that-made-dunkirk-audiences-nauseous-1.4311684); [Film Scalpel](https://www.filmscalpel.com/dunkirks-shepard-tone)). It is ideal for the 5-10 s "build" act. Keep it ≤ -18 LUFS short-term under the VO.
- A riser's peak momentary loudness stays at least 4 LU below the hit it feeds.
- Risers sweep straight through 1-4 kHz, so **they never overlap words**. Start them after the line's last word, as gap fillers, or use a `reverse_swell` (shorter, darker).

### 4.6 Epic vs intimate palettes

| | **intimate** (confession, memory, grief) | **epic** (reveal, manifesto, breakthrough) |
|---|---|---|
| hits | `heartbeat(n=1)`, `impact_soft`, `glass_tap` in key, [ADD] `breath_in`, [ADD] `tabla_na` | `impact_big`, `sub_drop`, `flash_hit`, [ADD] `braam`, [ADD] `glass_shatter`, [ADD] `tabla_dha` + roll |
| transitions | `swish_small`, `ui_hover`, short `reverse_swell`, `air_zoom` at -6 | `whoosh_by`, `whoosh_slow`, `whip`, 4-beat `riser`, `air_zoom` at 0 |
| texture | `shimmer` -10, [ADD] `ember_crackle` -18 | `shimmer` -6, [ADD] `ghungroo`, `sparkle` |
| bed | `room_tone` -30, `night_air` -32, [ADD] `tanpura_drone` -28 | `night_air` -26 plus the score's sub drone |
| reverb | room or plate, RT60 0.6-1.2 s, sends low | hall, RT60 2.5-4 s, bigger sends |
| width | narrow and centred (cue `width` 0.6-0.8) | wide whooshes and tails (`width` 1.2-1.6) |
| sub | nothing above -24 LUFS momentary | a sub-weight hit on every world change |
| music | 70-85 BPM, felt piano, tanpura or harmonium, no drums | 100-150 BPM, taiko or dhol, 808, braam |

**Arc rule:** intimate → epic **once**, at the reveal. Return to intimate only for the resolve and CTA. Never ping-pong.

### 4.7 Desi textures, used tastefully

These are shared South Asian textures both audiences own: tabla, dholak, harmonium, sitar, tanpura, ghungroo, taali.
1. **One desi voice per reel** (tabla OR sitar OR harmonium OR dholak), plus at most a tanpura drone under it. Two lead desi colours read as a "Bollywood template".
2. **Punctuation, not wallpaper:** at most one desi accent per 2 bars in storytelling. A continuous groove (dholak or dhol) only in a celebration or hype drop, at most 4 bars.
3. **Tune it:** the tabla dayan (`na`, `tin`) and the tanpura to **Sa = the reel's tonic**. Sitar phrases stay in the reel's raga-mode (§5.3). Keep harmonium chords in the score's progression.
4. **Modern production:** dry and close desi sounds over a modern sub or 808 with tight reverb, never a stock reverb wash. Duck them under the VO like any MID sound.
5. **Signature moves:**
   - a **tabla tirakita roll** (8 strokes in 32nds, crescendo) into a reveal, then **"dha" on the drop**;
   - a **sitar meend** (a glide up a 4th or 5th) on a keyword or the underline draw-on (Y5);
   - a **harmonium bellows swell** as the pad's breath under a light-beam sweep (L7);
   - **ghungroo** shimmer instead of Western chimes for sparkles;
   - **taali** (claps) on 2 and 4 in a celebration bar;
   - a **tanpura drone** as the sound bridge of an emotional reel.
6. **Respect both audiences:** avoid devotional signifiers (temple bells, azaan-like melisma, bhajan or naat quotes) and anything that reads as one country's anthem. Qawwali taali and harmonium are shared Sufi heritage: use them sincerely, never as a joke.
7. **Instrument roles:**
   - Dholak: ghe = bass, na/ka = slaps.
   - Tabla: dha = a hit, tin = a soft pulse.
   - The animation-studio "Sitey" recipe (104 BPM, D major pentatonic) groove: **ghe on 0 and 8; gheLo on 6 and 11; na on 2, 10, 14; ka on 7 and 15** of 16 steps. That is a good starting pattern for the hype drop (from the installed `animation-studio` music cookbook).

### 4.8 [ADD] Custom SFX library `jawad_sfx.py` (shared by all five reels)

Pattern (sound-designer agent): each function returns `_finish(x, hit_s, level_db, name)`. `META` holds (category, character, use), and `register()` adds the sounds to `audio.SOUNDS` and is idempotent. Every new sound must pass `A.qc(...) == []` and get a spectrogram check.

| name | cat. | recipe (audio.py helpers) | hit | level |
|---|---|---|---|---|
| `tabla_na(sa)` | impact | `A.modal(0.6, [sa*k for k in (1,2,3,4,5,2.95)], [.30,.20,.14,.09,.06,.02], [1,.62,.46,.30,.16,.12], rng)` + an hp(3 kHz) noise click, τ 2.5 ms; `reverb('room', -18)` | 0.0 | -4 |
| `tabla_tin(sa)` | impact | modal ratios (1, 2, 3, 4), τ (.45, .2, .12, .08), amps (1, .3, .18, .08) + a softer click | 0.0 | -8 |
| `tabla_ge` | impact | `osc(88 + 42·(1−e^(−t/0.07)))` + 0.18·2nd harmonic, e^(−t/0.3) decay + an hp(700) click: the upward "wah" | 0.0 | -6 |
| `tabla_dha(sa)` | impact | 0.6·na + 0.55·ge | 0.0 | -2 |
| `tabla_roll(n, bpm, sa)` | transition | n strokes alternating na/tin ("ti-ra-ki-ta") in 32nds, crescendo -12 → 0 dB; **hit = one 32nd after the last stroke** (lands on the downbeat) | end | -6 |
| `dholak_ghe(pitch)` | impact | f(t) = (70 + 60·e^(−t/0.05))·pitch; body sin + 0.28·sin(1.52φ)·e^(−t/0.07); slap = lp(noise, 1200)·e^(−t/0.008); tanh(1.35·x) | 0.0 | -4 |
| `sitar_meend(sa, interval=5)` | texture | additive string: 30 partials, f_n = n·f(t) with a glide of +interval semitones over 0.25 s starting at 0.15 s; a_n = n^−0.8·(1 + 3·e^(−((n − k(t))/3)²)) with the **jawari** bright band k(t) = 6 + 18·(1 − e^(−t/0.4)); τ_n = 1.8/(1 + 0.08n); **sympathetic strings** = `A.reson` bank on the raga notes (q 60-90) mixed at -18 dB; `reverb('plate', -16)`. (Jawari physics: the curved bridge shifts the contact point, and 11-13 tarab strings ring sympathetically: [jawari science](https://www.tosslevy.nl/jawari/the-science-of-jawari/); [sympathetic-string model patent](https://patents.google.com/patent/US5468906)) | 0.0 | -6 |
| `harmonium_swell(notes, dur)` | texture | two reeds per note detuned ±4 cents, additive pulse series a_n = (2/(nπ))·sin(nπd) with d = .28/.30 up to 6 kHz; bellows (1 + 0.05·sin(2π·5.2t)); LP 900 + 2600·bright; nasal `bp` 1250 Hz at -9 dB; attack 0.25 s; **hit = the swell peak** | peak | -8 |
| `tanpura_drone(sa)` (bed) | bed | 4 strings Pa(¾·Sa) · Sa · Sa · Sa/2, plucked in a 1.2 s cycle; additive with a jawari band sweeping harmonics 4 → 30 over 2.5 s; τ 4-6 s; a seamless 12 s loop via `A.reverb_circular` + `A._bed_finish` | — | bed |
| `ghungroo` | texture | `A._grains(d, rng, 60, 4500, 9500, g_lo=.01, g_hi=.05, harm=.3)` + a few `A.modal` bells (5.2, 7.9, 11 kHz, τ .08) | 0.0 | -10 |
| `braam(f0)` | impact | additive saw stack f0, 2f0, 3f0, 4f0 (≤ 3 kHz); LP 300 → 1400 Hz in 0.25 s then → 500 Hz over the duration (STFT mask); tanh drive 3; bend -30 cents; brass formants `eq('peak', 500/1200, +4)`; `reverb('hall', -8)`. (Braam = a low brass tone stacked in octaves, distorted and bent down: [Ableton](https://www.ableton.com/de/blog/learn-how-to-make-high-impact-sounds-for-movies-and-trailers/)) | 0.02 | -2 |
| `shepard_riser(duration)` | transition | 7 octave partials f_k(t) = 55·2^(k + t/duration) wrapped mod 7 octaves, amplitude e^(−½·(log₂(f/600)/1.3)²), plus a `noise_band` sweep 300 → 6 kHz; **hit = end** | end | -6 |
| `razor_snip` | ui | `_click(0.3, rng, band=(3000, 9000), tau=.0015, modes=[(4200, .03, .5), (6800, .04, .35), (9100, .02, .2)], low=(180, .02, .4))` | 0.0 | -5 |
| `film_burn(dur)` | transition | `_crackle(rate=2500, lo=1500, hi=9000, env=p**1.5)` + `noise_band` hiss 2.5 → 7 kHz (p²) + a whump `_thump(…, 45, 60, …)` at the end; **hit = end** | end | -4 |
| `paper_tear(dur)` | transition | `_crackle(rate=4000, lo=1200, hi=7000)` shaped by 3 Gaussian "rips" + a low fibre band at 600 Hz | start | -6 |
| `glass_shatter` | impact | a `_click` transient + 50 `modal` glass grains (1.8-6 kHz, τ .02-.15) spread over 0.6 s with exponential density + `_thump` at 60 Hz + `reverb('plate', -12)` | 0.004 | -2 |
| `ember_crackle(dur)` | texture | `_crackle(rate=120, lo=1500, hi=8000, gdur=(.0005, .003))` + lognormal pops (6/s) + low roar `noise_band(fc=180, bw=1.4)` at -14 | start | -10 |
| `molten_pour(dur)` | texture | roar `noise_band` fc 420 → 260 + Minnaert bubbles at 120-300 Hz + a 6-12 kHz sizzle crackle | start | -6 |
| `ember_stroke(dur=.35)` | transition | `noise_band` fc 6 → 3 kHz, bw 0.8, a fast-attack envelope + `_crackle(rate=300, hi=10000)`: the marker-sizzle of the underline | start | -8 |
| `projector_rattle` (bed) | bed | 24 Hz sprocket ticks (`bp` noise 2-6 kHz, alternating accents) + a motor at 48/96/144 Hz with wow + hiss at -40; a 4 s seamless loop | — | bed |
| `record_scratch` | transition | `noise_band` fc 600 → 3500 → 900 (a back-and-forth curve), bw 0.6, rate wobble, 0.35 s | 0.0 | -4 |
| `breath_in(dur=.4)` | texture | `noise_band` fc 1800 → 900, bw 1.2, sin² swell; **hit = end** (the VO onset) | end | -12 |
| `ink_bloom` | transition | cue recipe: `seed_plip` (`rate` 0.55, `lp` 1800) + `reverse_swell(0.4)` (`lp` 800). No new code | — | — |

**Processing effects** (not catalog sounds: they need the real audio, so they live in score.py and the final-mix stage):
- `scrub(src, track, t0, t1)`: granular overlap-add. 25 ms Hann grains every 8 ms; the read position follows the picture's `SCRUB` track; each grain is resampled by |dp/dt| and reversed when dp/dt < 0; LP 6 kHz; -6 dB.
- `tape_rewind`: the same at −2× to −8× with LP 3 kHz.
- `tape_stop(x, t0, dur=0.45)`: read position p(t) = t0 + ∫(1−u)² dt (pitch and speed fall to zero), then silence.
- `data_crunch(x, t0, dur)`: 6-bit quantise + sample-and-hold to 8 kHz, at -6 dB.
- `stutter(x, t0, slice=1/16 note, reps=4)`.

### 4.9 Objective QA (no ears)

Commands from sound-designer and music-supervisor; `QA = plugins/reels-studio/skills/reels-production-playbook/qa_measure.py`.

| check | how | pass |
|---|---|---|
| cue sync | `python3 $QA cues master.mp4 cues.json`, plus frames n−1, n, n+1 at every hero cue | every hero onset within ±1 frame of its event frame |
| loudness | `A.mix` report + `ffmpeg -af ebur128=peak=true` on the master | -14 ±0.5 LUFS; TP ≤ -2.0 (wav) / -1.5 (AAC); LRA 5-9 |
| VO clarity | `A.loudness_curve` of VO vs music (and vs SFX) on voiced frames | music ≥ 8 LU below (median); SFX in VO windows ≥ 6 LU below |
| hero placement | `fit_under_vo` raises nothing | no HERO cue inside a VO window |
| drop-out | RMS of the master over [t0, t0 + 8 f] | < -60 dBFS (true silence) or only the designated held-breath element |
| reveal is the peak | time of `max_momentary_lufs` | within ±0.2 s of the reveal hit |
| sub stacking | spectrogram (`A.mix_overview`) below 60 Hz | no two sub tails overlapping more than 50 % |
| phone check | the master through `A.hp(x, 250, 4)` | the reveal hit loses ≤ 7 dB (audio.py's bass_enhance spec) |
| tonal SFX in key | `f0_of` of each tonal cue (after pitch) vs scale tones | within ±30 cents of a chord tone |
| loop seam | last 0.5 s vs first 0.5 s: spectral-flux continuity, no fade to -inf | the end bar resolves into frame-0 material |

---------------------------------------------------------------------------------------------------------------

## 5. Music design

**Default: an original score, procedurally composed in `score.py` [ADD].** It is ours (no licence risk) and on the grid (cuts, hits and VO land on bars). It also becomes a brand asset: posted as "Original audio", renamed with the hook phrase, e.g. "Bas ek chhota sa change · @jawad_mp4" (`hooks_retention_captions.md`), so every reuse links back to Jawad. The trending-audio path is an *alternative export*, tested and never baked in (§5.6).

### 5.1 Emotional arcs for 30-40 s

Four rules apply to every arc:
- **Cold open:** sound is already in motion on frame 0. The low-pass hold of ref1 builds pressure.
- **One drop:** on the reveal, after the drop-out.
- **Resolve:** strip back for the insight or CTA.
- **Loop bar:** the last bar returns to the cold-open material and cadences *into* bar 0 (VII → i or V → i), so Instagram's auto-loop feels intended. Never fade to silence or black.

**Arc A · "Confession → breakthrough"** (emotional; 75 → 150 double-time; 11 bars = 35.2 s)

| bars | t (s) | section | music | SFX / picture |
|---|---|---|---|---|
| 0-1 | 0.0-3.2 | cold open | tanpura or pad drone (LP 600 Hz) + felt-piano motif note 1 on frame 0 | hook line at ≤ 0.3 s; `velvet_hit` at f0; frame 0 works as a still |
| 1-4 | 3.2-12.8 | confession | piano motif ×2, pad enters bar 2, heartbeat-pulse 8ths from bar 3 | intimate palette; C6 rack focus, L1 leaks |
| 4-6 | 12.8-19.2 | stakes rise | pad LP opens 600 → 1800 Hz, sub enters bar 5, tabla `tin` on beats; 2-beat riser + tirakita roll in the last 2 beats | the re-hook near 45-50 % (≈ 16-17 s): 0.3-0.5 s VO silence |
| 5.875-6 (bar 5, beat 3½) | 18.8-19.2 | **drop-out** | silence ½ beat (12 f); only a breath | picture holds |
| 6-9 | 19.2-28.8 | **breakthrough (drop)** | **double-time feel (150)**: kick, 808, harmonium chords, motif an octave up on sitar or harmonium, `dha` on the downbeat | `dha_hit` / `ember_slam`; the reel's ★ transition |
| 9-10 | 28.8-32.0 | resolve | strip to piano + pad; the tonic withheld (ends on 5) | insight / CTA line |
| 10-11 | 32.0-35.2 | loop bar | the drone + motif note 1 return; VII → i into bar 0 | end card held ≥ 1.5 s over the living world |

**Arc B · "Story ladder"** (storytelling; 90 BPM; 13 bars = 34.67 s): hook 0-1 (0-2.67 s) · setup 1-3 · complication 3-5¾ (8.0-15.33) · **drop-out** 5¾-6 (15.33-16.0, 20 f) · reveal/drop 6-9 (16.0-24.0) · payoff 9-11 (24.0-29.33) · CTA + loop 11-13 (29.33-34.67). Music: pulse 8ths from bar 1, a 2-bar build with a filter opening, drop on bar 6, resolve on bar 9.

**Arc C · "Manifesto hype"** (150 BPM with a half-time feel until bar 8; 22 bars = 35.2 s): bars 0-8 are a half-time groove (kick on 1, clap on 3) under Y3 slams. **Drop 1 at bar 8 (12.8 s)**: double-time, dhol or dholak groove (≤ 4 bars). A breakdown at bars 12-16 (19.2-25.6 s: VO-heavy, drums out, pad + 808 only), ending in a 1-beat drop-out at 25.2 s. **Drop 2 at bar 16 (25.6 s)**. Outro and loop at bars 20-22.

**Arc D · "Comedy turn"** (client-feedback humour; 100 BPM; 15 bars = 36 s): a confident groove → **record scratch + dead stop at bar 6 (14.4 s)** + 1 beat of silence for the punchline VO → re-entry with pizzicato or plucks (light) → payoff groove at bar 10 → loop. Comedy timing is ours, so this reel stays on original audio.

**Arc E · "Craft reveal"** (before/after; 112.5 BPM; 16 bars = 34.13 s): a tension pulse (16ths at 4 frames, very quiet) and the D3 render bar as the build (bars 5-8). **100 % lands on bar 8 (17.07 s) = the drop**. Then a montage on 8ths (8 frames each) for bars 8-12, resolve at bars 12-14, loop at bars 14-16.

**Beatless mode** (ref2 dialect, for the most intimate reel): no pulse. Drone + pad + piano phrases follow the VO phrase map. Risers end on the light events, sub hits fall on world changes. The "grid" is the VO phrase ends: transitions go 0.1-0.4 s after a phrase ends (§5.5).

### 5.2 BPM by mood (frame-locked values first)

| mood | BPM | feel and instruments | references |
|---|---|---|---|
| grief, intimate confession | **72, 75** | felt piano, tanpura or harmonium drone, heartbeat; no drums | tender-memory shape: 70-90 BPM, no drop, held chord (animation-studio storytelling table) |
| nostalgia, warm memory | 80, 85.7 | lofi pulse, vinyl-free texture, sitar phrases | lofi 70-90 |
| storytelling (default) | **90**, 96 | 8th-note pulse, pad, piano motif, light percussion | ref2 is beatless; ref3 is about 118 |
| cinematic drive, aspiration | **100** | taiko or tom pulse, Lydian pads, braams | |
| montage, craft, SaaS | **112.5**, 120 | 16th tension pulse, clean kick, glassy plucks | ref1 = 127 |
| hype, velocity | **150** (or 144) | 808, phonk-style cowbell-free drums, dhol/dholak drop | velocity edits; phonk and drill typically run 130-160 |

Tempo and mode are the strongest emotional cues in music, with mode first and tempo second, and their effects add up. Slow + minor + soft + legato + low + dark is how listeners build "sad" ([Eerola, Friberg, Bresin 2013, Frontiers](https://pmc.ncbi.nlm.nih.gov/articles/PMC3726864/); [Durham EmoteControl study](https://dur.ac.uk/news-events/latest-news/2022/02/how-do-music-listeners-think-emotions-sound-like-in-music/)).

### 5.3 Keys, modes and raga colours

Western modes and Hindustani thaats/ragas share scales. Choosing the overlap gives a sound both a Western-trained ear and a desi ear read as "right".

| emotion | Western mode | raga colour (same notes) | tonic suggestion | progression sketch (original voicings) |
|---|---|---|---|---|
| longing, heartbreak, nostalgia | Phrygian (b2 b3 b6 b7) | **Bhairavi** (all komal: r g d n) | C# or D | i – bII – i (drone-based), sitar meend into the b2 |
| sad / serious / epic | Aeolian | **Asavari / Jaunpuri** | D (Sa ≈ 146.8 Hz) | i – VI – III – VII; sus2 colours |
| hopeful minor, Sufi warmth | **Dorian** (natural 6) | **Kafi** (folk, qawwali) | D or E | i – IV (the "Dorian lift") – i – VII |
| wonder, aspiration, dreams | **Lydian** (#4) | **Yaman** (tivra Ma, evening raga) | D or E | I – II/I ostinato over a pedal → vi – IV |
| dark majesty, dawn | double harmonic major | **Bhairav** (r d komal, G N shuddha) | C# or D | I – bII – I with a tanpura pedal |
| dusk tension / suspense | Lydian b2 (r, #4) | **Puriya Dhanashri** (r M# d) | D | a drone + tritone shimmer; resolves into Yaman at the reveal |
| playful, confident | Mixolydian | **Khamaj** | E or F | I – bVII – IV – I |

Rules:
- **Mind the VO register.** A male Hindi TTS voice has its F0 at about 100-150 Hz and its consonants at 2-4 kHz. While a line is spoken, keep pad and piano voicings **above ≈ 300 Hz** (from A3/C4), and the sub **below ≈ 90 Hz**. Bring the piano motif down to octave 4 only in VO gaps.
- **Set Sa = the reel's tonic for every desi or tonal SFX**, and the `logo_sting` `tone` too.
- **Modulation trick for the turn:** move from Aeolian to Dorian (raise the 6th) at the reveal. Hope enters without a key change. Or go from Puriya Dhanashri to Yaman (resolve the b2): tension → wonder.
- **Motif rules:**
  - 3-6 notes within an octave, one leap (a 5th or 6th), then stepwise.
  - The phrase ends on scale degree 5 (open) until the last bar; resolution to 1 is saved for the loop seam.
  - **Reuse the same motif in new costumes:** felt piano (intro) → harmonium (build) → sitar or piano an octave up (drop) → music box or felt piano (outro). Recurring motifs sound "scored" (installed `animation-studio` skill, `references/music-cookbook.md`; we take the method only).

### 5.4 `score.py` [ADD]: the original-score engine (design)

Owner: music-supervisor, with motion-toolkit-engineer for the module. It lives next to `audio.py` in `pipeline/jawad_reels/` and reuses audio.py's DSP. Each reel gets a `<module>_music.py` holding its `SCORE`. The same `SCORE` (bpm, bars, events) is imported by the reel module's timeline and by `cues()`: **one source of truth**, so picture, SFX and music cannot drift (the animation-studio "single score" principle).

```python
"""score.py - procedural ORIGINAL music for the Jawad reels (48 kHz stereo float, deterministic, numpy/scipy).
Builds stems from a SCORE dict, arranges them per section, ducks under the VO, gates drop-outs, writes stems +
beats.json. Reuses audio.py DSP (osc, modal, noise_band, lp/hp/bp/eq/reson, reverb, sidechain, loudness,
limiter_gain, bass_enhance, decorrelate, _write_wav)."""
import json, math, numpy as np, audio as A
SR = A.SR
NOTE = lambda n: 440.0 * 2 ** ((n - 69) / 12)                      # midi -> Hz
MODES = dict(aeolian=(0, 2, 3, 5, 7, 8, 10), dorian=(0, 2, 3, 5, 7, 9, 10), phrygian=(0, 1, 3, 5, 7, 8, 10),
             lydian=(0, 2, 4, 6, 7, 9, 11), mixolydian=(0, 2, 4, 5, 7, 9, 10), bhairav=(0, 1, 4, 5, 7, 8, 11),
             puriya_dhanashri=(0, 1, 4, 6, 7, 8, 11))

SCORE_EXAMPLE = dict(
    bpm=90, offset=0.0, bars=13, key_midi=50, mode='aeolian',          # D3 = Sa (146.8 Hz)
    prog=[('i', 2), ('VI', 2), ('III', 2), ('VII', 2)],                 # (degree, bars), cycled
    sections=[('cold', 0, 1), ('setup', 1, 3), ('build', 3, 5.75), ('dropout', 5.75, 6), ('drop', 6, 9),
              ('resolve', 9, 11), ('loop', 11, 13)],                    # in bars
    motif=[(0.0, 0, 1.0), (1.0, 3, 0.5), (1.5, 2, 0.5), (2.0, 7, 2.0)],  # (beat, semitones above Sa, beats): 1-b3-2-5 (open)
    desi='tabla',                                                       # ONE desi voice, or None
    beatless=False, vo_words=None,                                      # path to faster-whisper words json
    gains=dict(pad=-6, pulse=-10, piano=-3, sub=-8, kick=-4, perc=-8, desi=-8, fx=-8))

def clock(S):
    spb = 60.0 / S['bpm']
    T = lambda bar, beat=0.0: S['offset'] + (bar * 4 + beat) * spb
    return T, spb

def render(S) -> dict: ...             # {'pad', 'pulse', 'piano', 'sub', 'kick', 'perc', 'desi', 'fx'} (N, 2) float64
def arrange(st, S) -> dict: ...        # section envelopes, filter curves, roll, gates, tape_stop, restart_at
def mixdown(st, S, vo=None): ...       # see below
def export(S, name): ...               # <AUD>/<name>_music.wav + _music_<stem>.wav, <OUT>/<name>/beats.json, MUSIC md
def verify(name, S): ...               # beatgrid (tempo +-0.2 BPM, phase +-15 ms), LUFS, section RMS table
```

**Stem recipes (exact starting numbers):**

| stem | synthesis | arrangement role |
|---|---|---|
| **pad** ("ember pad") | Per chord tone: 6 band-limited saws (additive harmonics to 8 kHz) detuned (−12, −7, −3, +3, +7, +12) cents, split L/R. ADSR 0.9 / 0.3 / 0.85 / 1.4 s. **Time-varying low-pass** via an STFT mask `m(t, f) = 1/(1 + (f/fc(t))^4)` (A._stft/_istft; no zipper noise), with a 0.07 Hz LFO of ±12 % on fc. `A.decorrelate(…, 0.5)`, `A.reverb('hall', -10)`. Voicing: root + 5th + 9th, 3rd on top, nothing below A3 while the VO speaks. | cold: fc 600 Hz → build: 600 → 1800 → drop: 2400 → resolve: 1200. This *is* the ref1 "low-pass hold → drop" |
| **pulse** | 8th-note pluck: saw (×1.003) + square (×0.997), LP envelope 350 + 3200·e^(−t/0.05) Hz, decay 0.16 s, alternating Sa and Pa. Or a **tick pulse**: `A.sound('ui_tick', pitch=…)` on 8ths, +1 dB per bar (the watch-tick tension of Zimmer's *Dunkirk*) | from the setup on; sidechained to the kick |
| **piano** ("felt piano") | Additive per note: partials n = 1..14, f_n = n·f₀·√(1 + B·n²) with B = 3.5e-4 (×2 per octave above C5). a_n = n^−1.1·\|sin(0.12·n·π)\| (hammer position). τ_n = τ₀/(1 + 0.45n) with τ₀ = 2.8·√(261.6/f₀) s. **3 strings** detuned 0 / +0.8 / −0.6 cents (beating). Hammer noise: 3 ms, LP 3 kHz, at -18 dB. **Felt**: LP 2.2 kHz, attack 6 ms, plus a key "thock" (`A._thump` 80 Hz, 30 ms) at -30 dB. `reverb('plate', -12)` + `reverb('hall', -20)`. Humanise ±5 % velocity and ±8 ms timing, **except notes on sync points** | the motif. Felt piano is the default emotional colour; costume changes per §5.3 |
| **sub / 808** | f(t) = f₀·2^(7·e^(−t/0.035)/12), x = tanh(1.6·sin φ), decay 0.9 s, HP 30 Hz, `A.bass_enhance` (it must still read on phone speakers) | from the drop, on beats 1 and 3 (or the 808 pattern in hype) |
| **kick** | f(t) = 48 + 110·e^(−t/0.03), amp e^(−t/0.35), a 3 ms click bp 2-4 kHz, tanh drive 1.4 | the drop; it is also the sidechain key (separate stem) |
| **perc** | cinema tom/taiko `A.modal(1.5, [62, 98, 133, 171], [.55, .30, .18, .12], [1, .5, .3, .15])` + a slap (lp noise 1.5 kHz) + hall. Clap/taali: 3 bursts bp 900-6000 at 0/9/19 ms, each e^(−t/0.006), + a tail e^(−t/0.12) + plate. Hats: hp 7 kHz noise, 25 ms, 8ths at -30 (16ths in hype). **Roll**: snare or tabla 4ths → 8ths → 16ths → 32nds over the last bar before the drop, +12 dB crescendo | build and drop |
| **desi** | one of `jawad_sfx`: tabla (tin pulse / tirakita roll / dha), dholak groove (16-step pattern, §4.7), harmonium chords (gain about 0.08 per note, attack 0.08; doubling the motif an octave down is what makes it read desi), a sitar meend phrase, or a tanpura drone | §4.7 rules |
| **fx** | `riser`-like noise sweeps, `shepard_riser`, `braam`, reverse cymbal (a reversed hp-4 kHz noise burst with a falling LP), `downlifter` at section ends | builds and transitions. **The hero hit itself belongs to the SFX stem**, never doubled here |

**Processing in `arrange`:**
- `gate(t0, t1, fade=0.004)` is the drop-out, applied after the reverbs.
- `tape_stop(t0, 0.45)` and `restart_at(bar, at_t)` serve D9's "the music undoes too".
- `stutter(t0, 1/16, 4)` serves D6.
- `lp_memory(t0, t1, 900)` plus mono is the flashback filter for L6.

**`mixdown`** (VO-aware; the result goes to music-supervisor's final mix):
```python
from scipy.ndimage import uniform_filter1d
def vo_envelope(vo, win=0.05, smooth=0.08):                   # 0..1 "someone is speaking", smoothed
    p = uniform_filter1d(A._mono(A._st(vo)) ** 2, int(win * SR))
    lvl = 10 * np.log10(np.maximum(p, 1e-12))
    env = np.clip((lvl - (lvl.max() - 30.0)) / 20.0, 0, 1)
    return -A._ballistics(-env, 0.03, smooth)                  # audio.py's smoother: 30 ms attack, 80 ms release
def mixdown(st, S, vo=None):
    G = S['gains']; db = lambda k: A.undb(G.get(k, -6))
    beds = A.sidechain((st['pad'] * db('pad') + st['sub'] * db('sub') + st['pulse'] * db('pulse')),
                       st['kick'], depth_db=4.0, attack=0.005, release=0.18)      # pump under the kick
    mus = beds + st['piano'] * db('piano') + st['perc'] * db('perc') + st['desi'] * db('desi') \
        + st['fx'] * db('fx') + st['kick'] * db('kick')
    if vo is not None:                                         # frequency ducking: -4 dB at 2.5 kHz while speaking
        e = vo_envelope(vo)[:len(mus), None]
        mus = mus * (1 - e) + A.eq(mus, 'peak', 2500, q=0.7, gain_db=-4.0) * e
    for a, b in S.get('gates', []): mus = gate(mus, a, b, 0.004)                 # drop-outs, after reverbs
    mus *= A.undb((-18.0 if vo is not None else -16.0) - A.loudness(mus))
    return mus * A.limiter_gain(mus, -3.0)[:, None]            # -3 dBTP: headroom for the final mix
```
- Hand-off: music-supervisor's final mix applies `A.sidechain(mus, vo, depth_db=6)`, **not its default 9**, because score.py already dipped the speech band by 4 dB. That totals about 10 dB in the speech band and 6 dB elsewhere. Keep `sidechain(mus, sfx, depth_db=3)` so hero hits punch through.
- **Section RMS targets** for the music stem before ducking: cold -19 to -17 dB; build -15 → -13 (rising); drop-out −∞; drop -12 to -11; resolve -17 to -15; music LRA ≥ 6 LU. If the music measures as one flat level, the intro is too loud: lower the intro, not the drop (animation-studio cookbook mix targets).

**Exports:**
- `<WS>/audio/<reel>_music.wav` (48 kHz, 24-bit) and stems `<reel>_music_{pad,pulse,piano,sub,kick,perc,desi,fx}.wav`.
- `<WS>/out/<reel>/beats.json` = `{bpm, offset, bars, sections, events, hits: [{t, bar, beat, label, sync: 'av'|'a'|'v'}]}`.
- `pipeline/jawad_reels/MUSIC_<reel>.md`: the music map, key, Sa Hz, and the source (= "procedural score.py, original").
- `verify()` runs music-supervisor's `beatgrid.py`: tempo within 0.2 BPM, phase ±15 ms. Also the LUFS, true peak and section RMS table.

**CPU budget:** additive synthesis of about 300 notes × 14 partials over 35 s at 48 kHz takes seconds in numpy. Run it with `nice -n 10`, single-threaded. No GPU, no downloads.

### 5.5 Cutting on the grid (VO-first)

The VO is speech from a TTS model. It cannot be quantised like a drum, so **the grid is fitted to the VO, then the VO lines are nudged** (whole lines move; nothing is stretched more than 3 %):
1. TTS → faster-whisper word times. Phrases are words separated by gaps over 0.25 s.
2. Pick BPM from the frame-locked set inside the reel's mood band. Keep **bar 0 = frame 0** (offset 0) for the loop seam.
3. For each phrase, the *cut* it pre-laps goes on the nearest beat (section phrases on bar lines). The line then starts 4-9 frames before that beat. Each line moves by at most ±0.25 s, and the gaps between lines stay ≥ 0.12 s.
4. Stressed key words (the ones a Y3 slam or caption keyword lands on) fall within ±1 frame of a beat or 8th. Otherwise insert or remove a quantised pause (multiples of an 8th) *before* the line.
5. Picture: section changes on bar lines; hard cuts on beats; montage on 8ths; hero transitions in VO gaps (§4.1). The transition's **cut point** is on the grid; its start is `c − pre`.
6. Music comes from the same `SCORE`: the drop bar is the reveal bar, and the drop-out sits in the half beat before it.

```python
def fit_bpm(onsets, bpms=(72, 75, 80, 85.714, 90, 96, 100, 112.5), prelap=0.2, tol=0.07):
    """onsets: VO phrase start times (s). Score = phrases whose (onset + pre-lap) land within tol of a beat
    (bar-line hits count double). Offset fixed at 0 (bar 0 = frame 0). Returns (score, bpm, residuals)."""
    best = None
    for bpm in bpms:
        P = 60.0 / bpm; x = (np.asarray(onsets) + prelap) / P
        res = (np.round(x) - x) * P                              # shift needed per line (s)
        bar = (np.round(x) % 4 == 0)
        s = np.sum((np.abs(res) < tol) * (1 + bar))
        if best is None or s > best[0]: best = (s, bpm, res)
    return best                                                  # then move each line by res (|res| <= 0.25 s)
```
**Beatless reels:** skip steps 2-4. Transitions go 0.1-0.4 s after phrase ends (ref2 median about 0.3 s), all times are frame-quantised, and score.py runs in beatless mode.

**Hard grid rules:**
1. Section changes only on bar lines.
2. No cut within 2 frames of a word onset unless it is the on-word cut (§4.3).
3. Never two feature transitions within 2 bars.
4. Montage cuts no faster than 6 frames (an 8th at 150), except stroboscopic flicks of 2-4 frames (ref1's strobes, at most twice per reel).
5. The end card starts on a downbeat and holds ≥ 1.5 s settled.
6. The last bar resolves into frame 0.

### 5.6 The trending-audio path (an alternative, tested)

**Evidence:**
- Instagram's ranking signals for non-followers centre on **watch time, likes per reach and sends per reach** (Mosseri, Jan 2025, as summarised by [dataslayer](https://dataslayer.ai/blog/instagram-algorithm-2025-complete-guide-for-marketers) and [eclincher 2026](https://www.eclincher.com/articles/how-the-instagram-algorithm-works-in-2026)).
- Audio is not an official ranking signal. Trending audio can surface a reel on the sound's page ([socialk.it](https://socialk.it/en/blog/instagram-trending-audio-strategy)).
- One secondhand test claims +24 % views for trending audio over voice-over on the same content ([Postfa, citing Buffer](https://postfa.st/blog/instagram-trial-reels)). It is unverified, so treat it as a hypothesis to **test with Trial Reels** (shown to non-followers first; results after about 24 h; [Meta, Dec 2024](https://about.fb.com/news/2024/12/trial-reels-try-content-non-followers-first-see-what-perfoms-best)).

**Exports per reel** (delivery-packager):
1. `jawad_<reel>.mp4`: **original audio** (VO + SFX + score). Default post. Rename the audio to the hook phrase.
2. `jawad_<reel>_vo_sfx.mp4` / `.wav`: **VO + SFX only** at -16 LUFS, TP -2 dBTP, with SFX already ducked under the VO. Post this with an in-app trending track at **10-20 % volume**. Reels mixes the original audio and the added music with separate sliders ([Hollyland](https://store.hollyland.com/blogs/creator-hub/keep-original-audio-on-reels-with-music)).
3. `jawad_<reel>_instrumental.wav`: score + SFX without the VO, for re-cuts, remixes and as a reusable sound.
4. In `MUSIC_<reel>.md`: the **reveal time** and the instruction "start the in-app song so its first big downbeat lands at t = <reveal> s". The picture is on our grid, so the trending track only has to align at the reveal at that volume.

**Which kinds of trending audio fit each arc** (check the in-app trending list on posting day, because trends move within days; never name a specific song in a brief without checking):

| arc | fits | avoid |
|---|---|---|
| A confession → breakthrough | slowed + reverb Bollywood/ghazal **instrumentals**, felt-piano covers, acoustic "unplugged"-style instrumentals, ambient organ/piano covers | lyrics under the VO, trap drops before the reveal |
| B story ladder | lofi Hindi/Urdu instrumental flips, sitar-lofi, cinematic ambient pulses | four-on-the-floor EDM |
| C manifesto hype | phonk / drift-phonk, desi drill and Punjabi-beat **instrumentals**, dhol-trap | slow piano; songs whose hook lyric fights the slams |
| D comedy turn | **stay on original audio** (the punchline silence is ours); a meme sound only as a 1-2 s in-app sting | any bed that fills the punchline gap |
| E craft reveal | minimal tech-house, glitch-hop, "satisfying edit" beat tapes | vocal-heavy songs |

**Fit rule:** prefer tracks within ±3 % of the reel's BPM or at exactly 2× or ½×. Our cuts stay on our grid either way.

**Licensing:**
- Creator accounts get the full licensed library for organic, non-commercial posts. Business accounts are limited to commercially licensed audio, and the Meta Sound Collection (14,000+ royalty-free tracks) is the fallback.
- Paid promotion needs commercially cleared music, and licensed songs can be muted later if rights change ([Sociality 2026](https://sociality.io/blog/instagram-creator-account/); [Soundstripe](https://www.soundstripe.com/blogs/instagram-music-library)).
- The in-app picker is not a licence ([blckalpaca on GEMA](https://blckalpaca.at/en/knowledge-base/social-media/social-media-content-creation-formats/gema-instagram-music-reels-business)).
- **Never bake a trending song into the uploaded file.** Song-led reels go through the lyric-visualizer's licensing route (brand skill).

**Test protocol:**
- Post Trial Reel A (original audio) and Trial Reel B (`_vo_sfx` + trending track) with identical picture.
- After 24-72 h compare: 3-s hold, average watch time, sends per reach and non-follower reach.
- Decide only after at least 3 pairs, because small accounts are noisy.

---------------------------------------------------------------------------------------------------------------

## 6. The per-reel beat sheet (the format every brief uses)

Every reel brief (`BRIEF.md` section per reel) carries:
1. **a header line:** BPM, frame-locked check, DUR = N bars, key, Sa Hz, mode/raga, arc template, look, transition family + signature, palette (intimate/epic), desi voice, audio path (original or trending test);
2. **the beat sheet table**, one row per event, in time order;
3. **a machine-readable YAML twin** of the table. `<module>.py` (timeline constants), `<module>_sfx.py` (`cues()`) and `<module>_music.py` (`SCORE`) are generated from it, so picture, SFX and music share one source of truth.

### 6.1 Columns

| column | content | rule |
|---|---|---|
| `#` | row number | |
| `bar.beat` | grid position, e.g. `5.3½` | from `at(bar, beat)`; must be frame-exact for the frame-locked BPMs |
| `t (s)` / `f` | seconds (3 decimals) / frame number | `f = round(t*30)` |
| picture | world · shot · subject (cut-out + expression) · device · on-screen type (style, px) | verified copy only; type sizes per the brand skill |
| transition | **ID** (Section 3) · frames · ease · cut point | the cut point is on the grid; at most 4 features per reel; one family |
| SFX cues | `name@align gain pan (params)` | catalog or [ADD] names only; hero cues only in VO gaps |
| music | stem events: section, filter, enters/exits, roll, gate, drop, tape-stop | from `SCORE` |
| VO | the line in Roman Urdu as spoken + start–end (s) | J-cut lines start 4-9 frames before their cut |
| caption | the Roman Urdu caption chunk (1-4 words) or "(title)" when designed type shows the words | house spelling (`prior/captions_roman_urdu.srt`) |
| notes | QA hooks: safe-zone, measure, "hero in gap ✓", "drop-out true silence 8 f" | |

### 6.2 Worked example (DEMO, not one of the five concepts)

All VO and caption lines are placeholders for the hinglish-scriptwriter. The demo shows **one transition family** (editor-native D, plus L3 push glue), the drop-out at the 45 % re-hook, hero hits in VO gaps, J-cuts with small dark hits, and a loop-back.

**Header:** "3 baje ka render" · **90 BPM** (20 f/beat, 80 f/bar, frame-locked) · **DUR 13 bars = 34.667 s (1040 f)** · D Aeolian → Dorian lift at the drop · Sa = D3 146.83 Hz · Arc B (story ladder) · look `noir_ember` → `ember` at the drop · family **D (editor-native)**, signature **D1 playhead scrub ✂** · palette intimate → epic at bar 6 · desi voice: harmonium · audio: original score (the trending test uses `_vo_sfx`).

| # | bar.beat | t (s) | f | picture | transition | SFX cues | music | VO (Roman Urdu) | caption |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0 | 0.000 | 0 | black → monitor light ignites behind Jawad's cut-out (neutral, rim-lit FLAME); timeline glow | light-on 6 f (exposure ramp, no lift) | `ui_click@hit` -4 (editor sound before picture); `velvet_hit(0.0)` | cold: drone + pad LP 600 Hz | — | — |
| 2 | 0.0 +6 f | 0.200 | 6 | `J.HouseTitle('RAAT KE', 'teen baje')`: caps rise, keyword rises, underline draws on | — | `shimmer@hit` -10, hp 5500 (under VO) | — | L1 0.20–2.35 "Raat ke teen baje, render 99% pe atka tha." | (title) |
| 3 | 1.0 | 2.667 | 80 | macro: progress pill stuck at 99 % (`jw_mono` 72 px) | hard cut + L3 push | `impact_soft@hit` -6 (DARK, auto lp 1100: **a J-cut cut gets no hero hit**) | felt-piano motif enters | L2 2.467 (−6 f pre-lap)–4.9 "Phir client ka message aaya…" | client ka message |
| 4 | 2.0 | 5.333 | 160 | dark-glass phone UI; the message bubble slides in with the verified copy | **D5** window swap, 14 f, in_cubic exit / POP enter | `whoosh_fast` -6 · `card_slide` 0 · `glass_tap` -10 (pitch → A) | pulse 8ths enter; pad LP → 1000 | (gap 4.9–7.0: let the bubble read) | (UI text) |
| 5 | 3.3 | 10.000 | 300 | keycaps **Ctrl** + **Z** press; history panel steps back | **D9 ✂** press (beat 4 of bar 3) | `typing(n=2, cps=8)` -6 | `tape_stop(10.0, 0.45)` | L3 10.05–10.55 "Ctrl+Z… dobara." | Ctrl + Z |
| 6 | 4.0 | 10.667 | 320 | the rewind lands on a fresh, empty timeline | D9 restore + L3 push | [ADD] `tape_rewind` 10.0–10.667 -6 → `impact_soft` 0 | `restart_at(bar=1, at=10.667)` | — | — |
| 7 | 4.2 | 12.000 | 360 | the window pulls back; the playhead scrubs through v01…v07 on the monitor (12 Hz updates) | **D1 ✂** scrub 12.0–15.333 (100 f) | [ADD] `scrub` -6 · `ui_tick` per clip edge -12 · `ui_click@hit` 15.2 0 | **music drops out under the scrub** (the scrub is the music) | L4 12.2–14.8 "Har 'chhota sa change' ek nayi kahani hai." | nayi kahani |
| 8 | 5.3½ | 15.333 | 460 | the playhead snaps (SNAP spring) onto the marker **FINAL**; the picture holds (1 %/s push) | **drop-out 20 f** = the 45 % re-hook (44-46 %) | true silence 8 f, then [ADD] `breath_in` ending at 16.0, -14 | `gate(15.333, 16.0)` | — | *FINAL* (silent keyword) |
| 9 | 6.0 | 16.000 | 480 | push into the monitor: the finished, graded film frame fills the screen; the look flips to `ember` | D1 push-in completes (in_expo 10 f) | `ember_slam(16.0, riser_beats=0)` → `flash_hit` -3 · `impact_big` 0 · `sub_drop` -4 (**the reel's loudest moment**) | **DROP**: kick, sub, harmonium chords, Dorian lift (B♮), motif an octave up | (VO waits ≥ 0.3 s) | — |
| 10 | 7.0 | 18.667 | 560 | the same frame as a raw/log grey version; a render bar rises from the bottom | **D3 ✂** wipe 18.667 → 100 % at 21.333 (80 f, stepped Track) | `bar_grow@start` (dur 2.667) -8 · `ui_tick` on resumes -14 | riser (2 beats) → 21.333 | L5 16.35–18.4 "Client ko bas ek change dikhta hai…" | ek change |
| 11 | 8.0 | 21.333 | 640 | 100 % → toast "Ho gaya"; the graded frame breathes | L3 push (payoff) | `toast_chime@hit` -4 (pitch → D) · `impact_soft` -6 | drop bar 2 | L6 21.6–23.0 "…mujhe poori film." | *poori film* |
| 12 | 9.0 | 24.000 | 720 | 3 finished shots, one per beat | **D8** velocity cuts, 12 f each, on 9.0 / 9.1 / 9.2 | `whoosh_fast` -4 ×3 (pan ±0.4) · `impact_soft` -8 on the last | groove with harmonium stabs (no second desi voice) | (gap 23.0–26.9) | — |
| 13 | 10.0 | 26.667 | 800 | Jawad (smirk) cut-out + `J.HouseTitle('EDIT NAHI,', 'kahani')` | hard cut + L3 | `velvet_hit(26.667, pitch=pitch_to('glass_tap', 293.7))` | resolve: piano + pad only | L7 26.9–28.9 "Main edit nahi… kahani banata hoon." | (title) |
| 14 | 11.0 | 29.333 | 880 | end card: J ring mark, `J.signature`, CTA "Follow karo" | hard cut on the downbeat, settles SETTLE 17 f | `logo_sting` 0 (tone in D) | loop material begins: drone + motif note 1 | L8 29.6–30.3 "Follow karo." | Follow karo |
| 15 | 12.0 | 32.000 | 960 | the card holds settled (≥ 1.5 s); the monitor light glides back to the frame-0 composition | — | `room_tone` bed only | VII → i cadence into bar 0 | — | — |
| 16 | 13.0 | 34.667 | 1040 | END → loops to f0 (the f0 click falls on the next beat) | — | — | — | — | — |

Checks this demo passes:
- One family (D) plus glue.
- Feature transitions D9, D1, D3: 3, all at least 2 bars apart.
- Hero cues at 16.000 and 29.333 sit in VO gaps (the VO resumes ≥ 0.3 s later).
- The J-cut cut at 2.667 carries only a DARK cue.
- The drop-out is at 44 % (the re-hook).
- The loudest moment is at the reveal.
- One desi voice.
- Loop bar present; nothing fades to black or silence.

### 6.3 YAML twin (parsed into timeline constants, `cues()` and `SCORE`)

```yaml
reel: demo_3am
bpm: 90
bars: 13
key: {sa_midi: 50, mode: aeolian, drop_mode: dorian}
look: {open: noir_ember, drop: ember}
family: D
signature: D1
desi: harmonium
vo_words: workspace/jawad_reels/tts/demo_3am_words.json
rows:
  - {n: 1, at: "0.0", picture: "monitor light-on, cut-out neutral", tx: null,
     sfx: [{name: ui_click, gain_db: -4}, {stack: velvet_hit}], music: [{section: cold}]}
  - {n: 3, at: "1.0", tx: {id: L3}, sfx: [{name: impact_soft, gain_db: -6}],
     vo: {id: L2, prelap_f: 6}}
  - {n: 4, at: "2.0", tx: {id: D5, frames: 14}, sfx: [{name: whoosh_fast, gain_db: -6},
     {name: card_slide}, {name: glass_tap, gain_db: -10, params: {pitch: "to:A"}}], music: [{enter: pulse}]}
  - {n: 7, at: "4.2", tx: {id: D1, frames: 100}, sfx: [{fx: scrub, src: [4.0, 19.0, 11.2]},
     {name: ui_click, at: "5.3+0.8", gain_db: 0}], music: [{dropout_under: scrub}]}
  - {n: 8, at: "5.3.5", tx: {id: dropout, frames: 20}, sfx: [{name: breath_in, at: "6.0", gain_db: -14}],
     music: [{gate: ["5.3.5", "6.0"]}]}
  - {n: 9, at: "6.0", sfx: [{stack: ember_slam, riser_beats: 0}], music: [{section: drop}]}
  # ... one entry per table row
```
Loader rules: `at` is `bar.beat[.fraction]`, converted with `at(bar, beat)`. `"to:A"` means `pitch_to(name, note_hz('A'))`. Stacks expand to the §4.2 functions. After expansion, `fit_under_vo()` runs over all cues; it raises when a hero cue lands on a word.

### 6.4 Blank template (copy into each reel's brief)

```
REEL <n> · "<title>" · BPM <x> (<f>/beat, <f>/bar, locked ✓) · DUR <N> bars = <s> s (<frames> f) · key <Sa> <mode/raga>
arc <A-E | beatless> · look <open> → <drop> · family <C|M|Y|L|D|O> · signature <ID> · palette <intimate → epic @bar>
desi voice <one | none> · audio <original | trending test> · re-hook drop-out @ <bar.beat> (45-50 %) · reveal @ <bar.0>
```
| # | bar.beat | t (s) | f | picture | transition | SFX cues | music | VO (Roman Urdu) | caption | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0 | 0.000 | 0 | (frame 0 works as a still, sound-off) | | (sound already in motion) | cold open | starts ≤ 0.30 s | | |
| … | | | | | | | | | | |
| n | N.0 | DUR | | loops to f0 | | | resolves into bar 0 | | | |

### 6.5 Sound and transition sign-off (per reel, objective)

- [ ] **Grid:** every cut and hit time is frame-quantised and on its grid (beat, 8th, bar), or VO-phrase-locked in beatless mode.
- [ ] **Cut rule:** the HALF switch is in place. Frames c−1 and c show no blur across the cut. Exposure pushes leave the black level of the 1st-percentile luma unchanged (± 2 code values).
- [ ] **Budget:** one transition family, at most 4 features, at most 2 ★, no two features within 2 bars, D6/D7/strobes at most twice.
- [ ] **VO:** `fit_under_vo` raises nothing. J-cuts are 4-9 frames. Music is ≥ 8 LU under speech. SFX in VO windows are ≥ 6 LU under speech.
- [ ] **Drop-out:** at most 8 frames of true silence, or one held-breath element. The reel's maximum momentary loudness falls within ±0.2 s of the reveal hit.
- [ ] **Loudness:** -14 ±0.5 LUFS, ≤ -2.0 dBTP (wav), ≤ -1.5 dBTP (AAC), LRA 5-9.
- [ ] **Key:** tonal SFX, desi hits and `logo_sting` are within ±30 cents of the key. One desi voice.
- [ ] **Sync:** the `qa_measure.py cues` report has every hero within ±1 frame. `beatgrid.py` on the mix gives tempo within ±0.2 BPM and phase within ±15 ms (beat reels).
- [ ] **Loop:** the last bar cadences into bar 0. No fade to black or to silence. The end card holds ≥ 1.5 s.
- [ ] **Originality:** the picture shows no ref layouts, ref audio or toolkit-example looks, props or copy. The UI is a generic NLE (no third-party trade dress). The film-frame edge text is our own.
- [ ] **Exports:** original-audio master, `_vo_sfx` stem/master, `_instrumental` wav, `MUSIC_<reel>.md` with the reveal time for in-app song alignment.

---------------------------------------------------------------------------------------------------------------

## 7. Open questions for the lead

1. **Music licensing route:** the default is an original score from `score.py`. Should any reel be song-led (the lyric-visualizer's licensing route)? Is Jawad's account a **creator** or a **business** account? That decides whether the trending-audio test can use the full library.
2. **AI-voice disclosure:** the VO is TTS, so Meta's AI label applies (brand skill rule 4). This is a lead decision; it does not change the mix.
3. **[ADD] code owners:** `jawad_tx.py` (motion-toolkit-engineer), `jawad_sfx.py` (sound-designer), `score.py` (music-supervisor + toolkit engineer). None of them exist yet. Each recipe above is specified to the parameter, but every one needs its own self-test and spectrogram or contact-sheet check before a reel depends on it.
4. **Kenney CC0 SFX** (`workspace/brand_reels/sfx/library/kenney/`, downloaded by another agent) can serve as optional transient layers (UI, sci-fi, impact). They are CC0, so no licence issue. They are downloads, though: read them with `python3 -I`, keep them in their own folder, and check them with `A.qc` before use.
5. **ref3:** my tempo (about 118 BPM) is a quick spectral-flux autocorrelation estimate from my own 1.5 fps contact sheet; nobody has done a full teardown yet. Confirm it if ref3's music grid matters for a brief.

---------------------------------------------------------------------------------------------------------------

## 8. Sources

Repository (read 2026-10-08):
- `plugins/reels-studio/skills/saas-motion-styles/SKILL.md`, `recipes.md`
- `plugins/reels-studio/toolkit/TOOLKIT.md`, `core.py`, `audio.py`, `type3d.py`, `ui.py` docstrings
- `plugins/reels-studio/agents/sound-designer.md`, `music-supervisor.md`
- `pipeline/jawad_reels/jawad_kit.py`, `project.json`, `BRAND.md`
- `.claude/skills/jawad-brand-reels/SKILL.md`, `.claude/skills/video-motion-graphics/SKILL.md`
- `brand_reels/research/ref1_analysis.md`, `ref2_analysis.md`, `hooks_retention_captions.md`
- Installed skills, used for ideas and method only: `animation-studio` (music cookbook, instrument recipes), `motion-reel`, `remotion-markup` (`transitions.md`, `light-leaks.md`)
- My own measurements: spectral-flux tempo of ref1 (127.5 BPM), ref2 (no stable beat; agrees with `ref2_analysis.md`) and ref3 (about 118 BPM); a ref3 contact sheet at 1.5 fps; ref2's transition strips.

Web (fetched or searched 2026-10-08):
- CapCut, "Which CapCut transitions are trending in 2026?": https://www.capcut.com/help/capcut-transitions
- GraphicDesignJunction, "Video and motion creative trends 2026": https://graphicdesignjunction.com/2026/01/video-and-motion-creative-trends-2026/
- Uppbeat, "The most downloaded video transition effects": https://uppbeat.io/blog/motion-graphics/video-transitions/the-most-downloaded-video-transition-effects
- Adobe, "What is datamosh": https://adobe.com/uk/express/learn/blog/what-is-datamosh
- PetaPixel, "New Instagram policies target reposted content" (2026-04-30): https://petapixel.com/2026/04/30/new-instagram-policies-target-reposted-content/
- Planoly, "Instagram updates its original content policy": https://www.planoly.com/blog/instagram-updates-its-original-content-policy.md
- dataslayer, "Instagram algorithm 2025": https://dataslayer.ai/blog/instagram-algorithm-2025-complete-guide-for-marketers
- eclincher, "How the Instagram algorithm works in 2026": https://www.eclincher.com/articles/how-the-instagram-algorithm-works-in-2026
- Meta, "Trial reels" (Dec 2024): https://about.fb.com/news/2024/12/trial-reels-try-content-non-followers-first-see-what-perfoms-best
- Postfa, "Instagram Trial Reels" (cites a Buffer test, unverified): https://postfa.st/blog/instagram-trial-reels
- socialk.it, "Instagram trending audio strategy": https://socialk.it/en/blog/instagram-trending-audio-strategy
- Sociality, "Instagram creator vs business account 2026": https://sociality.io/blog/instagram-creator-account/
- Soundstripe, "Instagram music library": https://www.soundstripe.com/blogs/instagram-music-library
- blckalpaca, "GEMA, Instagram music, Reels for business": https://blckalpaca.at/en/knowledge-base/social-media/social-media-content-creation-formats/gema-instagram-music-reels-business
- Hollyland, "Keep original audio on Reels with music": https://store.hollyland.com/blogs/creator-hub/keep-original-audio-on-reels-with-music
- OpenClip, "LUFS for short-form": https://openclip.app/learn/lufs.md
- Joseph Nilo, "Dialogue loudness, LUFS, true peak for video": https://josephnilo.com/blog/dialogue-loudness-lufs-true-peak-video/
- IRPR Sound, "How sound design improves Reels": https://sounddesign.irpr.agency/guides/how-sound-design-improves-reels/
- IRPR Sound, "Ducking vs EQ separation": https://sounddesign.irpr.agency/compare/ducking-vs-eq-separation/
- Adobe Community, "Better automated ducking for music behind voice-overs": https://community.adobe.com/questions-544/tutorial-better-automated-ducking-for-music-behind-voice-overs-158467
- Ableton, "High-impact sounds for movies and trailers": https://www.ableton.com/de/blog/learn-how-to-make-high-impact-sounds-for-movies-and-trailers/
- Violet Recording, "Sound design for trailers": https://violetrecording.com/sound-design-for-trailers/
- Morphic, "How to layer sound effects": https://morphic.com/resources/how-to/how-to-layer-sound-effects
- Filmdaft, "What is a sound bridge": https://filmdaft.com/what-is-a-sound-bridge-in-film-definition-and-transition-guide/
- SpotlightFX, "J-cuts and L-cuts": https://spotlightfx.com/blog/what-are-j-cuts-and-l-cuts-professional-dialogue-editing-explained
- Wikipedia, "J cut": https://en.wikipedia.org/wiki/J_cut
- Salimpoor et al. 2011, Nature Neuroscience 14:257-262 (summary at BRAMS): https://brams.org/2011/01/09/salimpoor/
- Scientific American blog, "This is your brain on music": https://blogs.scientificamerican.com/scicurious-brain/repost-this-is-your-brain-on-music/
- Eerola, Friberg and Bresin 2013, "Emotional expression in music", Frontiers in Psychology: https://pmc.ncbi.nlm.nih.gov/articles/PMC3726864/
- Durham University, EmoteControl study: https://dur.ac.uk/news-events/latest-news/2022/02/how-do-music-listeners-think-emotions-sound-like-in-music/
- CBC, "Hans Zimmer explains the audio trickery of Dunkirk": https://www.cbc.ca/radio/q/blog/hans-zimmer-explains-the-audio-trickery-that-made-dunkirk-audiences-nauseous-1.4311684
- Film Scalpel, "Dunkirk's Shepard tone": https://www.filmscalpel.com/dunkirks-shepard-tone
- Toss Levy, "The science of jawari": https://www.tosslevy.nl/jawari/the-science-of-jawari/
- US patent 5468906, "Sound synthesis model incorporating sympathetic vibrations of strings": https://patents.google.com/patent/US5468906
- Nikon, "10 tricks to add pace and energy to your edits": https://www.nikon.co.uk/en_GB/learn-and-explore/magazine/tips-and-tricks/cut-to-the-chase-10-tricks-to-add-pace-and-energy-to-your-edits
- Wolfcrow, "In-camera transitions": https://wolfcrow.com/the-3-important-in-camera-transitions-in-filmmaking/
- Screendollars, "Match cut": https://screendollars.com/glossary/m/match-cut
- StudySmarter, "Match cut": https://www.studysmarter.co.uk/explanations/media-studies/filmmaking/match-cut/
- Adobe Community, "The math behind speed graphs": https://community.adobe.com/t5/after-effects-discussions/what-s-the-math-behind-speed-graphs/m-p/9597181

Notes on the sources:
- Most "2026 trend" sources are vendor or SEO pages, so the trend claims above are directional, not measured platform data.
- No Instagram loudness specification is published; -14 LUFS is a consensus figure.
- The +24 % trending-audio figure is secondhand and unverified, so Section 5.6 treats it as a hypothesis to test.
- PetaPixel returned HTTP 403 to a direct fetch, so the April 2026 originality-policy details come from search summaries of PetaPixel and Planoly.
- The Uppbeat page returned HTTP 429, so its ranking comes from a search summary.
