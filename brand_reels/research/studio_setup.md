# Studio setup: `jawad_reels` toolkit project, brand kit and the `ember` looks

Date: 2026-10-08. Roles run: reels-studio `new-reel-project` skill + `brand-kit-builder` + `motion-toolkit-engineer`
(plugin at `plugins/reels-studio`, used as the engine only). Nothing from the earlier toolkit clients (Organic
Fostering, Floret) is used: no example timelines copied, no footage, no props, no copy, and Jawad gets his own looks.

## 1. What was set up

| path | what |
|---|---|
| `pipeline/jawad_reels/*.py`, `TOOLKIT.md` | project copy of the toolkit code (`cp -n`; no `examples/`, no `LOCAL_SETUP.md` / `bootstrap_wsl.sh`) |
| `pipeline/jawad_reels/project.json` | project `jawad_reels`, workspace `workspace/jawad_reels` (git-ignored via `workspace/`), site `https://www.instagram.com/jawad_mp4/`, palette roles, fonts, logo, delivery `reel/jawad_reels` prefix `jawad` |
| `pipeline/jawad_reels/BRAND.md` | palette + roles, contrast table, fonts, logo rules, safe zones, banned claims, open questions, restore block |
| `pipeline/jawad_reels/brand_src/` | derived wordmark: `logo_full.svg` (= `logo_src`), `logo_mark.svg/.png`, `logo_wordmark(.svg/.png)`, `logo_wordmark_onDark(.svg/.png)`, builder `make_logo.py` (text outlined from the brand fonts) |
| `pipeline/jawad_reels/jawad_kit.py` | brand profile: looks `ember` + `noir_ember`, house type styles, ui looks, footage grades, helpers (underline stroke, title lockup, signature, embers), `register_look()`, self-test |
| `pipeline/jawad_reels/brand_smoke.py` | 2 s smoke module on `ember` (renamed from the skill's `smoke.py`) |
| `workspace/jawad_reels/` | fonts (14 TTF), `brand/` (logos, specimen sheets, cover crops, brand sheet), `out/selftest/`, `out/brand_smoke/`, `logs/` |

Dependencies: `pip install cairosvg fonttools` (cairosvg 2.9.1, fonttools 4.66.1). Already present: Python 3.13.16,
numpy, opencv, pillow, scipy, bpy 5.2.2 LTS, ffmpeg, git-lfs 3.4.1.

`setup_workspace.py` ran fonts + brand only (Google Fonts css2 + gstatic downloads work). The site-photo scrape is
skipped by the new `"site_images": false` key (instagram.com answers 429 and is a JS app); `--footage` is never
run (no Drive folder; it now refuses without `drive_folder` instead of falling back to the old client's folder).
Re-verified: a rebuild into a scratch workspace (`FOSTER_WS=<tmp> python3 setup_workspace.py` + restore block)
gives byte-identical `logo_full.png`, `logo_full_onDark.png` and fonts; the font check prints all True.

## 2. Palette (project.json; toolkit role names kept, Jawad tokens added)

Measured from his covers (`workspace/brand_reels/prior/*cover*.jpg`): keyword orange #F07124 / #EB711E / #EE5E0B,
keyword top #F4A21A-#FB8626, bottom #CD5024 / #F84600, underline core #FAC68E-#FEE3B3, red haze #952D10, white
type #E9E0D7, blacks #000000-#0C0109 / #080B10, OpenArt warm brown #2E0E03-#38160A.

| token (role key) | hex | role | contrast on NIGHT_1 |
|---|---|---|---|
| FLAME (MAGENTA, LOGO_MAGENTA) | `#FF6A1A` | primary: keyword glow, accents, active UI, rims | 6.8 |
| HOT_PINK | `#FF8A3D` | hot-orange highlight: rims, neon tubes | 8.3 |
| RED (ORANGE, LOGO_ORANGE) | `#F2312B` | accent: fire red, gradient ends, rim hot spots | 4.85 |
| EMBER | `#B3120E` | deep ember red: haze, halos (never text on dark) | 2.8 |
| AMBER | `#FFB547` | hot amber: keyword tops, underline core, sparks | 11.0 |
| GOLD (LEAF) / LEAF_HI | `#FF9F1C` / `#FFD38A` | secondary warm gold: ticks, secondary glows | 9.4 |
| PLUM | `#4A0E08` | oxblood panels, inner shadows | - |
| SMOKE | `#2A1A15` | smoky glass / cards (IVORY on it 15.3) | - |
| NIGHT_0 / NIGHT_1 | `#070404` / `#170A07` | warm blacks (the world) | - |
| INK | `#0B0706` | dark text on light / on FLAME + AMBER (7.0 / 11.4) | - |
| IVORY | `#FFF3E6` | white text (never pure white) | 17.7 |
| ASH | `#A8978C` | secondary text on dark | 6.9 |
| PEACH / LAVENDER | `#FFD3B0` / `#F4E4DA` | soft warm tints (light cards) | - |

Fails (do not use): IVORY on flat FLAME 2.6, FLAME on IVORY 2.6, AMBER/GOLD on IVORY, EMBER text on dark 2.8.
IVORY on RED 3.66 = heroes only. Keyword gradient (top to bottom): `#FFC34D -> #FF8A1F -> #F04A16`.

## 3. Fonts

| role | font | evidence |
|---|---|---|
| serif-italic keyword | **Instrument Serif Italic** (OFL; single weight) | specimens next to cover crops (`workspace/jawad_reels/brand/spec_*.png`): y/g/f/d/A shapes and the narrow italic match "yaadein", "younger self", "AI video ad"; Playfair, Cormorant, DM Serif Display, Fraunces, Lora, Bodoni Moda, Newsreader, Libre Caslon, Gelasio rejected |
| grotesk | **Poppins** SemiBold / Bold / Medium (+ Black for `display`) | "MEETING MY" (SemiBold, +6 % tracking), "delete" (SemiBold), "@jawad_mp4" (Medium) match; Montserrat, Plus Jakarta Sans rejected |
| mono (UI, timecode) | **JetBrains Mono** Medium / Bold | chosen |

`font_map`: Nunito -> Poppins, Poppins -> Poppins, Caveat -> InstrumentSerif; `font_copies` writes
`InstrumentSerif-Bold.ttf` (= RegularItalic) so the toolkit's accent role `Caveat-Bold` / `font='hand'` is the
serif italic. Kit aliases (type3d + ui): `serif`, `serif_roman`, `grotesk`, `grotesk_bold`, `grotesk_medium`, `mono`,
`mono_bold`. Instrument Serif is Latin-only (fine for Roman Urdu / Hinglish); Poppins covers Devanagari; Urdu
Nastaliq would need Noto Nastaliq Urdu (not set up).

## 4. Looks and how to use them

```python
import jawad_kit                                   # FIRST (applies the profile; idempotent; workers re-import it)
from jawad_kit import K, T, ui, F, S3, SFX, J
DUR, LOOK, BPM = 34.0, 'ember', 100                # or 'noir_ember'
cv = K.background(LOOK, t, cam)                    # bokeh=0..1 scales the warm bokeh layer
J.HouseTitle('MEETING MY', 'younger self').draw(cv, t, 540, 700, t0=1.2)   # caps -> keyword rise -> underline
T.render('yaadein', 'jw_key', px=200).draw(cv, 540, 900)                   # the keyword alone
J.underline(760).draw(cv, 160, 1010, u=K.ramp(t, 1.0, 1.7, 'inout_cubic'))
win = ui.app_window(w=760, h=600, look=LOOK, title='edit_room.prproj', header='Render queue')   # ember glass
J.signature(cv, 540, 1585); J.embers(140).draw(cv, cam, t)
def post(cv, t): return K.post(cv, LOOK, t)        # crush / mono / grain order handled by the kit
```

- **`ember`**: deep warm-black void (NIGHT_0, warm base tint), flame key glow top-right with smoky curtains, ember
  haze low-left, faint stage haze from the top, warm floor bounce, 22 drifting bokeh discs (big ones only FLAME/RED,
  dimmer with size). Post: bloom 0.62 (threshold 0.40) tinted (1.0, 0.46, 0.20), halation 0.16, vignette 0.50, chroma
  1.2, grain 0.016, no black lift, `crush=(0.010, 0.015, 0.020)` per-channel toe `c^2/(c+k)` (warm shadows, blacks
  pushed down, never lifted). ui look: smoky warm glass, FLAME accent, FLAME->RED gradient, hot-orange rim with red
  hot spot, GOLD ticks. Footage grade `F.GRADES['ember']`: contrast 1.22, black 0 (no lift), warm shadows, orange
  highlights.
- **`noir_ember`**: monochrome warm black with one red-orange practical light (top right) and a SMOKE fill; post
  `mono=0.85` (everything not orange/red goes to warm mono), deeper crush, vignette 0.62, grain 0.022. Grade: sat 0.40,
  contrast 1.35.
- **House type styles**: `jw_key` (keyword), `jw_key_core` + `jw_key_halo` (the same split for per-glyph animation,
  verified equal to `jw_key` within 1/255), `jw_key3d`, `jw_neon`, `jw_caps`, `jw_caps_bold`, `jw_body`, `jw_mono`,
  `jw_handle`. Existing presets re-tinted (their hard-coded hex): extrude3d sides `#7A1A0C` + warm ivory face,
  chrome sides, deep_glow fill, ink_soft, glass_pill_light shadow.
- **Safety defaults**: every ui function that defaulted to `look='neon'` now defaults to `'ember'`;
  `ui.app_window` title/header default to empty, `ui.button` to "Follow", `ui.badge` to "@jawad_mp4",
  `T.Counter(prefix='')` (no £). Always pass real copy anyway.
- **More looks**: `J.register_look('jw_inferno', base='ember', bg={...}, post={...}, bokeh=(...), ui_look={...},
  grade={...})` gives the colorist's `jw_*` looks the same backdrop table, bokeh and finish (crush/mono/grain order).
  The colorist's `G.finish` can call `K.post(cv, look, t, grain=0)`: the kit then skips grain and still applies
  mono + crush.
- The built-in `neon` / `amber` / `airy` now render in Jawad's colours (palette roles) but keep the old clients'
  structure (planet rim, dot grid): do not use them for Jawad.

## 5. Self-tests (all `nice -n 10`, in `pipeline/jawad_reels/`, images in `workspace/jawad_reels/out/selftest/`)

| test | result |
|---|---|
| `core.py selftest` | OK, 15 s; typical frame (no footage) 0.36 s at 1 sample; backgrounds / DOF / glow / particles / motion blur sheets in the new palette |
| `type3d.py selftest` | OK, 20 s; hero extrude draw + sweep 40 ms; footage tiles (`_video_sheet`, `_hook_sheet`) skipped: no footage in this workspace |
| `ui.py selftest` | OK, 18 s; steady-state animated window frame 176 ms; media tiles skipped (no footage) |
| `audio.py selftest` | OK, 66 s; catalog + demo mixes -18.0 LUFS, true peak -1.7 dBTP, QC problems: none |
| `jawad_kit.py selftest` | `jawad_kit_ember.png`, `jawad_kit_noir_ember.png` (title lockup + glass window + embers + signature), `jawad_kit_type.png` (all house styles + underline) |
| `render.py brand_smoke` | sheet + stills + 2 s range render; looked at and compared with `prior_covers.jpg`: white grotesk caps over a flame serif keyword with the underline comet, warm black world, on-brand |

The self-tests' own sample copy is the toolkit's fixture text from the earlier client (internal test images only).

## 6. Measured render cost (`brand_smoke`, ember look, 1 worker, shared 4-core box under load 5-6)

TIMINGS_PLACEHOLDER

Component costs (warm caches, 1 core, median of 5): `K.background('ember')` ~40-80 ms (bokeh layer ~0-35 ms;
`neon` 53 ms), `K.post('ember')` ~130 ms (`neon` 138 ms in the same run; crush 27 ms), `K.post('noir_ember')`
~210 ms (mono 100 ms), `to_srgb8` 39 ms, HouseTitle settled ~58 ms, rising ~240 ms (was ~430 ms before the
core/halo split), underline draw-on 8 ms, 110 embers 1 ms, glass window plane + rows ~60-180 ms.

## 7. Commands

```bash
cd pipeline/jawad_reels
python3 setup_workspace.py                                   # fonts, logo_full(.png/_onDark); site photos skipped
WS=$(python3 -c "import core; print(core.WS)")
cp brand_src/logo_mark.png brand_src/logo_wordmark.png brand_src/logo_wordmark_onDark.png "$WS/brand/"
nice -n 10 python3 jawad_kit.py selftest                     # branded showcase
nice -n 10 python3 core.py selftest   # also type3d / ui / audio
nice -n 10 python3 render.py brand_smoke --sheet 4 --samples 1 --workers 1
nice -n 10 python3 render.py brand_smoke --range 0 2 --samples 3 --workers 1   # -> out/brand_smoke/render_stats.json
python3 brand_src/make_logo.py                               # rebuild the wordmark SVG/PNGs
python3 ../../plugins/reels-studio/skills/new-reel-project/brandkit.py sheet project.json --out "$WS/brand/brand_sheet.png"
```

## 8. Problems found and fixes (project copy only; the plugin toolkit is untouched)

1. **Glyph animators ignored their `blur=`** (`type3d.Glyphs._run`): `blur` was taken as a draw kwarg, so
   `g.rise(..., blur=7)` blurred the settled word for good while the animator used its default. Fixed: `blur` goes
   to animators that have one (rise / slam / track); `block_blur=` blurs the whole block. Regression check: rise,
   slam, track, typewriter(blur=3), wipe without an animator blur -> max diff 0.0 against the old routing; only
   `rise(blur=7)` changes (the bug). Upstream-worthy.
2. **type3d / ui self-tests crashed without footage** (they read the old client's clips c11 / c04 / c08-c12). Now
   they skip those tiles when `frames/manifest.json` is missing. Upstream-worthy.
3. **setup_workspace.py fell back to the old client** for footage (its Drive folder) and scraped `site` for photos.
   Added `"site_images": false`, `--footage` refuses without `drive_folder`, and `"font_copies"` for single-weight
   families. Upstream-worthy.
4. **Underline comet head strobed** into 3 dots with 3 motion-blur samples on a fast draw-on: the head is now spread
   along its shutter path (`smear`, HouseTitle computes it from the draw-on speed).
5. **Per-glyph 0.8 em glow** made the keyword rise ~2x more expensive: HouseTitle draws `jw_key_core` per glyph and
   `jw_key_halo` once (same pixels when settled).
6. First keyword pass looked pink/washed (fill gain 1.3 + inner glow under the shoulder); re-measured the covers and
   moved to an un-boosted amber -> orange -> red-orange fill, soft bevel, 0.8 % stroke, red-orange glow.
7. Plugin notes (not fixed, not ours to edit): `brandkit.py sheet` prints the old client's sample line ("Could you
   make room?") and its layout overlaps the logo row when the palette has > 18 keys; `ui.money()` defaults to `£`;
   `Style` dataclass default `side_tint #8E1E68` still applies to custom styles built from `flat` with depth.

## 9. Open items for the lead

- `.gitattributes` LFS lines from the skill were not written (shared repo file): add
  `reel/jawad_reels/*_master.mp4`, `media/jawad_reels/*.tar`, `media/jawad_reels/footage/*`,
  `media/jawad_reels/music/*` with `filter=lfs diff=lfs merge=lfs -text` when deliveries start.
- Ask Jawad: approve or replace the derived wordmark; confirm Instrument Serif Italic + Poppins (measured, not
  confirmed); currency (Rs / ₹) for any number on screen; Urdu script ever needed.
- The colorist's `jw_*` looks should be built with `J.register_look(...)` on top of `ember` (or `noir_ember`).
