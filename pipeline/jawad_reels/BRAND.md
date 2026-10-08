# Jawad (@jawad_mp4) - brand kit for the reels toolkit

Personal brand of Jawad, video editor / motion designer (video editing, motion graphics, AI video, cinematic
storytelling) for a Pakistani + Indian audience. Voice-over and captions in Hinglish / Roman Urdu.
Profile: https://www.instagram.com/jawad_mp4/ (not scraped: instagram.com rate-limits with 429; every value
below is measured from his own covers or derived from them).

Sources (measured 2026-10-08): `workspace/brand_reels/prior/prior_covers.jpg` and the three 1080x1920 covers
`openart_awards_cover`, `you_made_it_cover`, `yaadein_spiderman_cover` in the same folder.

## House style (what the covers do)
- One **glowing serif-italic keyword** per line, amber-gold at the top of the letters to orange to red-orange at
  the bottom, with a tight orange glow and a wide red halo ("yaadein", "younger self", "AI video ad", "better.").
- Paired with **white grotesk** words: uppercase above the keyword ("MEETING MY", "MY ENTRY", "KUCH") or
  lowercase on the same line ("delete ... hoti", "You're ...").
- A **glowing underline stroke** under the keyword: thin on the left, thicker to the right, hot comet head.
- Warm, dark cinematic worlds: black / very dark warm backgrounds, bokeh and floating specks, red-orange rim
  light on subjects, haze.
- Signature `@jawad_mp4` in small Poppins Medium at the bottom.

## Palette (project.json "palette")
Toolkit role names are kept (the code uses them); Jawad's own token names are added (FLAME, RED, EMBER, GOLD, ASH, SMOKE).

| key | hex | role for Jawad | measured / derived |
|---|---|---|---|
| MAGENTA, LOGO_MAGENTA, **FLAME** | `#FF6A1A` | primary: keyword orange, accents, active UI, glows | measured: keyword mid-tones #F07124 / #EB711E / #EE5E0B, pushed a step for emissive glow |
| HOT_PINK | `#FF8A3D` | bright hot-orange for rims, glow highlights, neon tubes | derived (lighter FLAME) |
| ORANGE, LOGO_ORANGE, **RED** | `#F2312B` | accent: fire red (gradient ends, rim hot spots, second glow) | derived from the keyword's red-orange bottom (#F84600 / #CD5024) and the red haze; brightened to pass 4.5:1 on NIGHT |
| **EMBER** | `#B3120E` | deep ember red: haze, wide halos, rims. Never text on dark | derived from the red glow behind "younger self" (#952D10) |
| AMBER | `#FFB547` | hot amber highlight: keyword top, underline core, sparks | measured: underline core #FAC68E-#FEE3B3, keyword top #F4A21A |
| LEAF, **GOLD** | `#FF9F1C` | secondary warm gold: success ticks, secondary glows | derived (between FLAME and AMBER; Jawad has no green) |
| LEAF_HI | `#FFD38A` | pale gold highlight | derived |
| PLUM | `#4A0E08` | deep oxblood for dark panels / inner shadows | derived |
| INK | `#0B0706` | dark text on light / on FLAME and AMBER buttons | derived (warm black) |
| NIGHT_0 | `#070404` | darkest warm black (void) | measured: cover blacks #000000-#0C0109, #080B10 |
| NIGHT_1 | `#170A07` | second background black | derived (warm, between the void and #2E0E03 of the OpenArt cover) |
| **SMOKE** | `#2A1A15` | warm smoky glass / card base | derived |
| IVORY | `#FFF3E6` | white text (warm white) and light backgrounds | measured: white type #E9E0D7 under the grade |
| **ASH** | `#A8978C` | secondary text on dark (6.9:1 on NIGHT_1) | derived |
| PEACH | `#FFD3B0` | soft warm tint for light cards | derived |
| LAVENDER | `#F4E4DA` | soft warm blush tint (name kept for the role) | derived |

Gradient "flame" (keyword fill, top to bottom): `#FFC34D` -> `#FF8A1F` -> `#F04A16` (measured on the covers).

### Contrast (WCAG; body >= 4.5, hero >= 3)
| pair | ratio | use |
|---|---|---|
| IVORY on NIGHT_0 / NIGHT_1 | 18.7 / 17.7 | all white text |
| FLAME on NIGHT_0 / NIGHT_1 | 7.1 / 6.8 | orange text on dark: OK at any size |
| RED on NIGHT_1 | 4.85 | OK (heroes and body) |
| AMBER on NIGHT_1 | 11.0 | OK |
| ASH on NIGHT_1 / SMOKE | 6.9 / 5.9 | secondary text |
| IVORY on SMOKE (glass) | 15.3 | UI text |
| INK on FLAME / AMBER | 7.0 / 11.4 | text on orange / amber buttons |
| IVORY on EMBER | 6.4 | white text on ember-red buttons |
| IVORY on RED | 3.66 | heroes only (>= 130 px) |

**Do not use:** IVORY on flat FLAME (2.6), FLAME on IVORY (2.6), AMBER/GOLD on IVORY (1.6/1.9), EMBER as text on
dark (2.8; glows and rims only). `ui.button` uses the look gradient (FLAME -> RED) with white text: for button copy
pass `grad=('RED', 'EMBER')` or keep the label >= 40 px with its shadow, or use INK text.

## Fonts (project.json "font_map" / "google_fonts" / "font_copies")
| role | family | why |
|---|---|---|
| keyword (serif italic) | **Instrument Serif Italic** (Google Fonts, OFL) | specimens rendered next to the cover crops: the y / g / f / d / A shapes, the narrow italic and the ball terminals match "yaadein", "younger self", "AI video ad" almost exactly (Playfair, Cormorant, DM Serif, Fraunces, Lora, Bodoni Moda, Newsreader, Libre Caslon, Gelasio compared and rejected). The covers look a touch heavier: jw_key adds a 0.8 % em stroke + glow. |
| grotesk (uppercase + lowercase lines, handle) | **Poppins** SemiBold / Bold / Medium (OFL) | matches "MEETING MY", "delete", "@jawad_mp4" (the t cut, single-storey a, round G). Montserrat and Plus Jakarta Sans compared. |
| mono (UI, timecodes) | **JetBrains Mono** Medium / Bold (OFL) | chosen (no mono on the covers). |

font_map: `Nunito -> Poppins` (toolkit display face: Black / ExtraBold / Bold), `Poppins -> Poppins` (UI),
`Caveat -> InstrumentSerif` (the accent role; `font_copies` writes `InstrumentSerif-Bold.ttf` = the italic, because
Instrument Serif has a single weight). jawad_kit adds the aliases `serif`, `serif_roman`, `grotesk`,
`grotesk_bold`, `grotesk_medium`, `mono`, `mono_bold` and points `hand` at the serif italic.
Scripts: Instrument Serif is Latin only (Roman Urdu / Hinglish are fine); Poppins also covers Devanagari.
For Urdu Nastaliq script captions add `Noto Nastaliq Urdu` (not set up).

Type sizes (1080x1920): keyword 150-260 px, grotesk line 72-110 px (uppercase +6 % tracking), UI 34-46 px,
fine print >= 28 px, signature 30-36 px.

## Logo (no official logo exists - derived house wordmark)
`pipeline/jawad_reels/brand_src/` (committed), built by `brand_src/make_logo.py` from the brand fonts (text is
outlined, so the SVGs need no fonts):
- `logo_full.svg` (= project.json `logo_src`): stacked lockup, serif-italic "Jawad" in the flame gradient
  (GOLD -> FLAME -> RED), the glowing underline stroke, `@jawad_mp4` in Poppins Medium INK.
  setup_workspace.py renders `<WS>/brand/logo_full.png` and the derived `logo_full_onDark.png` (INK -> white).
- `logo_mark.svg/.png`: "J" monogram in a thin flame ring.  `logo_wordmark.svg/.png` (INK) and
  `logo_wordmark_onDark.svg/.png` (IVORY): one line "JAWAD" grotesk + "mp4" serif italic.
Rules: the logo is a derived proposal, ask Jawad to approve it before it closes a reel; never recolour, stretch
or add effects to it beyond the glow of the look; on dark use the onDark files; min width 280 px; keep one
cap-height of clear space.

## Looks (jawad_kit.py)
`import jawad_kit` first in every module (`from jawad_kit import K, T, ui, F, S3, SFX, J`), then use
`LOOK = 'ember'` or `'noir_ember'`. Details in `pipeline/jawad_reels/jawad_kit.py` and the research note
`brand_reels/research/studio_setup.md`.
- `ember`: deep warm-black void, flame key glow top-right, ember haze low-left, warm bokeh, red-orange bloom
  tint, halation, grain 0.016, crushed (never lifted) warm blacks.
- `noir_ember`: near-monochrome warm black with a single red-orange practical light; non-red colours are
  desaturated in post; deeper crush, more grain.
- The built-in `neon` / `amber` / `airy` looks belong to earlier clients; with this palette they render in
  orange/red but keep their old structure (planet rim, dot grid). Do not use them for Jawad.

## Toolkit colours project.json cannot reach (handled in jawad_kit.py)
| hard-coded | where | now |
|---|---|---|
| extrude3d `side_tint #8E1E68`, fill `#D8CEDA` | type3d STYLES | `#7A1A0C` sides, warm ivory fill |
| chrome sides `#8E1E68 / #16051A` | type3d STYLES | `#7A1A0C / #140504` |
| deep_glow fill `#FFF1F8` | type3d STYLES | `#FFF4E8` |
| ink_soft fills / sides / shadows (`#3C2740` ...) | type3d STYLES | warm browns |
| glass_pill_light shadow `#5B2E52` | type3d STYLES | `#4A1A10` |
| LOOKS bloom_tint / black_tint | core | new looks `ember`, `noir_ember` (own tints, no black lift) |
| ui `amber` look tint `#2A1208` | ui | not used (ui looks `ember` / `noir_ember` added) |
| Style dataclass default `side_tint #8E1E68` | type3d | still there for custom styles built from `flat` with depth: pass `side_tint='#7A1A0C'` |
| `ui.money()` symbol `£`, `ui.app_window` / `button` / `badge` default copy | ui | defaults re-pointed to neutral copy; pass `symbol=` to money (Rs / ₹) |
| `brandkit.py sheet` sample line "Could you make room?" | plugin helper | the earlier client's sample text; internal sheet only |

## Safe zones (Instagram Reels 1080x1920)
Key copy x 70..1010, y 230..1480. Nothing textual below y 1620 (caption + UI). Avoid x > 930 for y 1050..1700
(action buttons). Signature at y 1560-1600, centred. Keep faces and keywords off the top 230 px (status bar,
"Reels" header).

## Copy facts
- Handle `@jawad_mp4`; profile URL above. Language: Hinglish / Roman Urdu (see
  `workspace/brand_reels/prior/captions_roman_urdu.srt` for his caption style).
- No other facts (follower counts, clients, prices, awards) are verified: do not state any.

## Banned / avoid
- Claiming wins or rankings (the OpenArt cover says "MY ENTRY", not a win), invented client names, view or
  follower numbers, earnings promises.
- Third-party logos and IP (OpenArt, Spider-Man, Adobe / Premiere UI) in his reels; use generic UI.
- Anything from the earlier toolkit clients (Organic Fostering / Floret): their copy, props (houses, hearts,
  £ coins), footage (c00-c18) and looks.

## Open questions (for Jawad)
1. Approve or replace the derived wordmark (`brand_src/logo_*`); does he have a logo / monogram already?
2. Confirm the fonts (Instrument Serif Italic + Poppins measured from his covers) and whether he owns a
   commercial original he wants us to use.
3. Confirm the hexes (measured from compressed JPG covers, so +-5 % in tone).
4. Currency / units for any numbers on screen (Rs vs ₹), and whether captions ever need Urdu script.

## Restore block (after a fresh clone / container reset)
```bash
pip install cairosvg fonttools                      # + numpy opencv-python-headless pillow scipy, bpy 5.2 (Py 3.13)
cd pipeline/jawad_reels
python3 setup_workspace.py                          # fonts (+ font_copies), logo_full(.png/_onDark); site photos skipped
WS=$(python3 -c "import core; print(core.WS)")      # -> <repo>/workspace/jawad_reels
cp brand_src/logo_mark.png brand_src/logo_wordmark.png brand_src/logo_wordmark_onDark.png "$WS/brand/"
cp -n "$WS/fonts/InstrumentSerif-RegularItalic.ttf" "$WS/fonts/InstrumentSerif-Bold.ttf"   # setup does it too
python3 brand_src/make_logo.py                      # only to rebuild the logo SVG/PNGs after a design change
python3 jawad_kit.py selftest                       # branded showcase -> $WS/out/selftest/jawad_kit_*.png
```
Never run `setup_workspace.py --footage` without a `drive_folder` of Jawad's (it now refuses).
