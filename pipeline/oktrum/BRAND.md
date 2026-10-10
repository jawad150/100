# Oktrum brand kit (reels toolkit)

Written by the brand-kit builder, 2026-10-10. Sources: the logo file `brand_src/logo.png` (1563 px RGBA, transparent;
the artwork itself is 1102 x 287 px), the site CSS tokens the lead read into `INTAKE.md` section 2, and the site hero
art `workspace_oktrum/intake/site/poster.jpg`. oktrum.com cannot be fetched from this container, so nothing here was
re-scanned from the live site. Copy facts, CTAs and banned claims live in `INTAKE.md` section 3: use them as written there.

Brand sheet: `workspace_oktrum/out/brand/sheet.png` (palette by group, gradient, type roles, logo on the three
backgrounds, contrast table).

## 1. Palette (project.json `"palette"`)

Measured = read from the logo pixels or the site CSS. Derived = made for a toolkit role the brand does not define.

| key | hex | role in the toolkit | source |
|---|---|---|---|
| MAGENTA = BLUE | `#5170FF` | primary: hero fills, buttons, key glows, neon blobs | measured: CSS primary; logo dot sphere is exactly #5170FF (median of 2173 opaque dot px) |
| LOGO_MAGENTA = VIOLET | `#8465F4` | logo gradient start (toolkit "logo pair" first colour) | measured: CSS; logo wordmark left edge #8462F4..#8468F3 |
| HOT_PINK | `#81AAFF` | bright light blue for glows / highlights on dark | measured: CSS extra blue |
| ORANGE = CYAN = LOGO_ORANGE | `#81D4E6` | accent, gradient end, rims, ticker highlights | measured: CSS; logo wordmark right edge exactly #81D4E6 |
| LEAF = VIOLET | `#8465F4` | secondary (ui `ok` colour, LEAF-based fills) | measured: CSS |
| LEAF_HI | `#B4A3FF` | bright violet | derived (lighter VIOLET) |
| BLUE_HOVER | `#6180FF` | hover / lighter primary | measured: CSS |
| BLUE_MID | `#4A65FF` | pressed button, small text on dark >= 4.5 only on #000 | measured: CSS |
| BLUE_DEEP | `#3A55E0` | blue text and small buttons on the light look | measured: CSS |
| PLUM | `#2A2370` | deep violet-navy for dark panels, neon blob, inner shadows | derived |
| INK = NAVY | `#07091A` | dark text on light; site navy-black background | measured: CSS background |
| NIGHT_0 | `#020309` | darkest top of the night gradient | derived (near-black tinted navy; site also uses #000) |
| NIGHT_1 | `#0A0E2A` | night gradient bottom (a step above #07091A so the gradient reads) | derived |
| IVORY | `#F3F6FF` | cool white: light text on dark, page of the light look | derived (cool white for the light look) |
| PEACH | `#CFDBFF` | pale blue bloom / card tint on the light look | derived |
| LAVENDER | `#E4DCFF` | pale violet bloom / card tint on the light look | derived |
| AMBER | `#F2C46D` | soft gold, only for the gold-asset beat (XAU, gold bar) | derived (not a brand colour) |
| UP | `#34D399` | ticker up, P&L positive (on dark) | measured: CSS |
| DOWN | `#F87171` | ticker down, P&L negative (on dark) | measured: CSS |
| UP_DEEP | `#047857` | ticker up on the light look | derived (UP fails on #F3F6FF) |
| DOWN_DEEP | `#B91C1C` | ticker down / crash candle on the light look | derived (DOWN fails on #F3F6FF) |

**Brand gradient**: 135 deg, violet `#8465F4` -> cyan `#81D4E6` (the wordmark). In type3d:
`fill=('VIOLET', 'CYAN'), fill_angle=-45` (135 deg CSS = top-left to bottom-right) or `('LEAF', 'ORANGE')` by role.
A three-stop version for big fills: `('VIOLET', 'BLUE', 'CYAN')`.
**Glass card** (site): white 4 % fill, border rgba(129,212,230,.12) = CYAN at 12 %.
The site's visual world (poster.jpg): particle dot sphere, neon cyan-blue rings, candlesticks, particle waves, grid floor.

Role names in the toolkit are historical (MAGENTA, ORANGE, LEAF...). In new code prefer the alias keys
`BLUE VIOLET CYAN NAVY UP DOWN` (same hexes) so the intent is readable.

## 2. Contrast (WCAG; body >= 4.5, heroes >= 130 px and button labels >= 40 px semibold >= 3)

| text | on #000000 | on #07091A | on #F3F6FF |
|---|---|---|---|
| #FFFFFF / IVORY #F3F6FF | 21.0 / 19.4 | 19.8 / 18.3 | **fail** 1.1 / 1.0 |
| BLUE #5170FF | 5.11 | 4.81 | 3.80 hero only |
| HOT_PINK #81AAFF | 9.13 | 8.59 | **fail** 2.13 |
| CYAN #81D4E6 | 12.5 | 11.8 | **fail** 1.56 |
| VIOLET #8465F4 | 5.15 | 4.84 | 3.78 hero only |
| LEAF_HI #B4A3FF | 9.62 | 9.05 | **fail** 2.02 |
| BLUE_MID #4A65FF | 4.60 | 4.32 hero only | 4.23 hero only |
| BLUE_DEEP #3A55E0 | 3.56 hero only | 3.34 hero only | 5.47 |
| AMBER #F2C46D | 12.9 | 12.1 | **fail** 1.51 |
| UP #34D399 / DOWN #F87171 | 10.9 / 7.59 | 10.3 / 7.14 | **fail** 1.78 / 2.56 |
| UP_DEEP #047857 / DOWN_DEEP #B91C1C | 3.83 / 3.25 hero only | 3.60 / 3.05 hero only | 5.08 / 5.99 |
| INK #07091A | fail | fail | 18.3 |
| PLUM #2A2370 | fail | fail | 12.4 |

Buttons: white on BLUE 4.11 (OK for the 40 px+ semibold CTA label, not for small text); white on BLUE_DEEP 5.91 and
on BLUE_MID 4.57 (small text OK); INK on CYAN 11.8; INK on UP 10.3; white on UP 1.92 and white on DOWN 2.77 (never).

**Do not use**: any light colour (IVORY, HOT_PINK, CYAN, LEAF_HI, AMBER, UP, DOWN) as text on the light look;
BLUE / VIOLET for body text on the light look (heroes only, or use BLUE_DEEP); BLUE_DEEP, UP_DEEP, DOWN_DEEP as
small text on dark; white text on UP / DOWN chips (use INK); the gradient wordmark straight on #F3F6FF (see 4).

## 3. Fonts (project.json `"font_map"` / `"google_fonts"`; all Google Fonts, OFL)

| role | family / weights | toolkit names that resolve to it |
|---|---|---|
| display (heroes, kinetic type, 3D type) | **Inter Tight** Black / ExtraBold / Bold (400-900 present) | `Nunito-*`, type3d `display`, `display2`, `display_bold` |
| UI / body | **Inter** Regular / Medium / SemiBold / Bold | `Poppins-*`, type3d `ui`, `ui_bold`, `body`, `medium`, ui.py text |
| editorial accent | **Instrument Serif Italic** | `Caveat-Bold` and type3d `hand` (file copy, see restore block); or `InstrumentSerif-RegularItalic` directly |
| tickers, prices, numbers | **JetBrains Mono** Regular / Medium / Bold | by file name: `JetBrainsMono-Medium` etc. (no alias) |

Rules: Inter Tight is the voice of the brand (site display face). Instrument Serif Italic is a creative addition
(lead's call, not on the site): **one word per beat**, mixed into an Inter Tight line ("Trade with *precision.*",
"*Blink.*"), never a whole sentence, never in UI chrome. It has a single weight, so it is the same file under the
`-Bold` name; do not fake-bold it. JetBrains Mono only for numbers and ticker rows. The wordmark's own letters
(Montserrat-like) are NOT a font we set type in: never re-typeset "Oktrum"; use the logo files.

Check (all True, 2026-10-10): `Nunito-Black/ExtraBold/Bold -> InterTight-*`, `Poppins-Regular/Medium/SemiBold/Bold ->
Inter-*`, `Caveat-Bold -> InstrumentSerif-Bold.ttf` (= the italic), `JetBrainsMono-Bold`. A test render of `hand`
gives the serif italic.

## 4. Logo

Files in `workspace_oktrum/brand/` (all at the artwork's native resolution; there is no vector source):

| file | what | made by |
|---|---|---|
| `logo_full.png` | 1102 x 287, dot sphere + gradient wordmark, transparent | setup_workspace.py from `brand_src/logo.png` |
| `logo_full_onDark.png` | identical to logo_full (`logo_dark_lum: 0.0`: the logo has no dark parts, it is designed for dark) | setup_workspace.py |
| `logo_mark.png` | 244 x 287, the halftone dot sphere only (soft dot falloff on the left is part of the art) | cropped, committed in `brand_src/` |
| `logo_wordmark.png` | 815 x 153, "Oktrum" gradient wordmark only | cropped, committed in `brand_src/` |
| `logo_wordmark_ink.png` | the wordmark in INK #07091A, same alpha | **derived**, fallback for the light look only, needs client approval |

Usage rules:
- Never recolour, re-typeset, stretch, outline, bevel or redraw the wordmark or the sphere. The gradient is the logo.
  The ink wordmark is the only derived variant, for the light look, and only once the client approves it.
- Dark looks: use the original on NIGHT/NAVY/black. Over busy art, bloom or footage, put a **dark pool** behind it
  (a soft NAVY radial or glass plate at >= 70 % behind the wordmark) so the violet start keeps >= 4.8:1. No bloom
  across the wordmark (keep it below the post bloom threshold, or draw it after a reduced-bloom pass).
- Light look (#F3F6FF): the gradient fails there (cyan end 1.56:1, violet start 3.78:1). Preferred: the original logo
  on a navy glass plate (rounded NAVY card, radius ~ 0.25 x plate height, logo inset >= 0.5 x mark height). Fallback
  (after approval): dot sphere original + `logo_wordmark_ink.png`.
- Minimum size: full logo >= 420 px wide on a 1080 frame (wordmark cap height ~ 60 px); mark alone >= 120 px tall.
  Maximum without upscaling: 1102 px wide (it is a raster); larger than ~1.2x looks soft, so for a huge hero use the
  3D dot-sphere mark from Blender, not an upscaled PNG.
- Clear space: the height of the "O" (about 0.5 x logo height) on every side; no text or UI inside it.
- End cards: logo yaw-0 (flat logo, or the 3D dot sphere resolving to yaw 0 next to the 2D wordmark).

## 5. Restore block (after a container reset)

```bash
cd pipeline/oktrum
python3 -c "import setup_workspace as s; s.fonts(); s.brand()"      # fonts + logo_full / logo_full_onDark (no site_images)
WS=$(python3 -c "import core; print(core.WS)")
cp brand_src/logo_mark.png brand_src/logo_wordmark.png brand_src/logo_wordmark_ink.png "$WS/brand/"
cp "$WS/fonts/InstrumentSerif-RegularItalic.ttf" "$WS/fonts/InstrumentSerif-Bold.ttf"   # 'hand' / Caveat-Bold -> serif italic
python3 -c "import os,core; [print(w, os.path.exists(core.font_path(w))) for w in ('Nunito-Black','Nunito-ExtraBold','Nunito-Bold','Poppins-Regular','Poppins-Medium','Poppins-SemiBold','Poppins-Bold','Caveat-Bold','JetBrainsMono-Medium')]"
```
Verified 2026-10-10: a scratch `brand()` rebuild plus these copies is byte-identical to the workspace
(`logo_full`, `logo_full_onDark`, `logo_mark`, `logo_wordmark`, `logo_wordmark_ink`). Do not run `site_images()`
(oktrum.com is blocked here); the intake files in `workspace_oktrum/intake/` come from the lead.

## 6. Hard-coded toolkit colours still in the old (magenta/orange/plum) brand

project.json re-points everything that reads `core.C` by role name. These do not, and must be overridden in an Oktrum
profile (motion-toolkit-engineer, `oktrum_kit.py`); suggested values in linear RGB or Oktrum hex:

core.py
- `K.LOOKS['neon']` `bloom_tint=(1.0, 0.62, 0.86)` (pink) -> cool blue, e.g. `(0.55, 0.72, 1.0)`;
  `black_tint=(0.0016, 0.0003, 0.0018)` (plum) -> navy `(0.0006, 0.0009, 0.0024)`.
- `K.LOOKS['amber']` `bloom_tint=(1.0, 0.72, 0.42)`, `black_tint=(0.0020, 0.0008, 0.0002)` (warm): a reel using it
  needs a navy/cyan cinematic variant (e.g. bloom `(0.60, 0.85, 1.0)`, black tint as neon).
- `K.LOOKS['airy']` `bloom_tint=(1.0, 0.85, 0.80)` and `'natural'` `(1.0, 0.9, 0.85)` (warm pink) -> `(0.85, 0.90, 1.0)`.
- `_BG_LOOKS['neon']` `rim=('ORANGE', 'AMBER', 1.0)`: now a cyan -> gold planet rim; Oktrum wants `('ORANGE',
  'HOT_PINK', 1.0)` (cyan -> light blue) or `rim=0`.
- `_BG_LOOKS['amber']` `base_tint=(1.35, 0.8, 0.4)` (orange cast on the base gradient) and `rim=('AMBER', 'ORANGE')`,
  blob colours ORANGE / AMBER / LOGO_ORANGE: the look turns cyan + gold on brown; replace with a cool tint
  (e.g. `base_tint=(0.85, 0.95, 1.25)`) and blobs BLUE / CYAN / VIOLET if a reel uses it.
- `_BG_LOOKS['airy']` blobs include `AMBER` (gold tint on the light page) and HOT_PINK: swap AMBER for CYAN/BLUE at
  low intensity.
- `Particles` default colours are role-based (`IVORY, PEACH, HOT_PINK`: cool white / pale blue / light blue, fine);
  only the selftest passes AMBER. Pass `colors=` explicitly if you want gold dust.

type3d.py (`T.STYLES`)
- `extrude3d`: `side_tint='#8E1E68'` (Style default, l.481) and fill `#F3EEF3 / #D8CEDA` (pinkish whites) -> side
  `PLUM`/`NAVY`-based (e.g. `side=(('#3A3FA8', 1), ('#0A0E2A', 1))`), fill `#FFFFFF / #EEF2FF / #D2DAF0`.
- `chrome`: `side=(('#8E1E68', 1), ('#16051A', 1))`, `env_ground='#FF9A6A'`, fill `#F4EEF4` -> side
  `(('#2A2370', 1), ('#07091A', 1))`, env_ground `#81D4E6`, fill `#F3F6FF`.
- `gold`: fill `#FFF1D2 / #FFC46A / #F08A1E`, rim `#FFD9A0`, `env_ground='#FFB15C'`, inner shadow `#7A2A00`, side
  `#9A3A06 / #1E0802`: fine for the gold-asset beat only (XAU); do not use for brand words.
- `deep_glow`: fill `#FFF1F8` (pink white) -> `#F3F6FF`; glow colours follow roles.
- `ink_soft`: fill `#3C2740 / #2A1A2D`, side `#6E2A60 / #4A1A44`, long shadow `#8A5070`, shadow `#5B2E52` (all plum)
  -> fill `#07091A / #141A3A`, side `#2A2370 / #1A1850`, long shadow `#5A6AB0`, shadow `#2A2370`.
- `glass_pill_light`: `pill_shadow_color='#5B2E52'` -> `#2A2370` (pill tint PEACH now = pale blue, fine).
- Far side colour `col('#1A0518')` in the extrude renderer (l.1090): plum-black far side -> `#05071A`.
- `Counter(prefix='£')` (pound sign default, l.1921 and the selftest): Oktrum numbers need `prefix=''` or `'$'`
  per beat (e.g. `0.2` PIPS, `0%`, `40+`, balance `0.00`).
- Selftest / demo presets at l.2124-2130 and l.2314-2317 (`#7A2E68`, `#3A1436`, `#4A1242`, `#C23A84`, `#7A3A5A`): plum;
  ignore unless copied.

ui.py
- `amber` look: `tint_top=mix('#2A1208', PLUM)`, `tint_bot='#0E0604'` (brown glass) -> use `neon` look, or override to
  NAVY/PLUM. Its `grad_hi`/`rim` use AMBER (gold rims): avoid the amber ui look for Oktrum.
- `neon` look `grad_hi=(HOT_PINK, AMBER)`: light blue -> gold highlight gradient; override to `(HOT_PINK, CYAN)`.
  Same for `airy`. airy `rim`/`glow` = PEACH (pale blue, OK).
- Default copy that must never appear: `money(symbol='£')`, `app_window(title='organicfostering.co.uk',
  header='Am I eligible to foster?')`, `button(text='Start your enquiry')`, `badge(text='Rated Good by Ofsted')`,
  `search_bar(placeholder='Search support')`, the `pound` icon, demo dock tiles ('Weekly Allowance', '£447.60') and the
  `('#FFE2C4', '#FFB15C')` money gradient in the docstring/selftest. Oktrum copy: title `oktrum.com`, buttons
  "Open Live Account" / "Try Demo Free" / "Get Started", badges "PCI DSS Compliant" / "Bank-Tier Encryption" /
  "Negative Balance Protection".

assets3d (Blender)
- `assets3d_hero.py` `BRAND` dict (l.112) is a hard-coded copy of the old palette and does not read project.json
  (LOGO_MAGENTA #A6055E, LOGO_ORANGE #F46308 ...). New Oktrum Blender assets must take colours from
  `core.PALETTE_HEX` / this file, not from that dict.

## 7. Open questions (for the client, via the lead)
1. Is there a vector (SVG/AI) logo and an official light-background version? Today we only have a 1102 px raster;
   the light look needs either a navy plate or the derived ink wordmark (`logo_wordmark_ink.png`): may we use it?
2. What is the wordmark typeface (looks like Montserrat SemiBold)? Only matters if they want type set in it; we will
   not re-typeset the logo.
3. Instrument Serif Italic is our creative addition, not a site font: OK with the client?
4. Gold (AMBER #F2C46D) is used only for the gold-asset beat; confirm no brand gold exists.
