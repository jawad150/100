---
name: floret-motion-kit
description: Build or change Floret Capitals motion graphics (spots, reels, covers, UI animations) with the installed cinematic toolkit. Use for any Floret video work - new scenes or timelines, General Sans typography, liquid-glass UI, SaaS UI kit widgets (app window, chips, charts, toasts, buttons, cursors), 3D gold objects, orbit text, SFX, stills, contact sheets and final renders.
---

# Floret motion kit

Two layers live in this repo:

1. **The Organic Fostering toolkit** (`pipeline/fostering/`, documented in `pipeline/fostering/TOOLKIT.md`):
   compositor + effects (`core`), typography (`type3d`), SaaS UI kit (`ui`), 3D sprite loader (`sprites3d`),
   footage (`footage`), procedural SFX library (`audio`), parallel renderer (`render`).
2. **The Floret profile** (`pipeline/floret/kit.py`): `import kit` installs that toolkit for Floret without
   editing it - 1248 x 1248 @ 60 canvas, General Sans fonts, gold palette, `gold` (dark) and `pearl` (light)
   looks, gold type styles, outputs in `workspace4/`. Never edit `pipeline/fostering/` for Floret needs; extend
   `kit.py` instead (another project depends on the toolkit as it is).

The existing 36 s spot is `pipeline/floret/floret.py` (its own compositor: liquid-glass slabs that refract the
background, liquid colour blooms, letter-by-letter `Title`, `orbit()` ring text, `hero()` 3D object shots).
Reuse its functions when extending the spot; use the kit for new pieces.

## Start a new piece

Copy `pipeline/floret/kit_demo.py` (the module contract: `DUR, LOOK, BPM, draw(t), post(cv, t), samples(t),
cues(), prewarm()`; `draw` is a pure function of t). Then:

```bash
cd pipeline/floret
python3 kit.py sheet mypiece 12                         # contact sheet in the canvas aspect
python3 kit.py render mypiece --stills 1.0,2.5 --jpg    # full-quality stills
python3 kit.py render mypiece --preview                 # quick motion check
python3 kit.py render mypiece                           # master + share mp4 + SFX mix
python3 kit.py selftest                                 # Floret showcase of the kit
```
Outputs: `workspace4/kit_out/<module>/`, SFX in `workspace4/audio/`. Vertical Reels: `FLORET_W=1080 FLORET_H=1920
FLORET_FPS=30 python3 kit.py ...` (or `kit.canvas(1080, 1920, 30)` before building sprites).

## Brand

- Colours (`K.C[...]`, linear): `GOLD #E49F38`, `GOLD_HI #F7D08A`, `GOLD_LO #B06A1C`, `CHAMPAGNE #FFF1D6`,
  `BRONZE`, `ONYX_0/ONYX_1` (black stage), `SILVER`, accents `ELECTRIC` blue, `PSX_GREEN`, `PMEX_RED`, `PEARL`.
  The toolkit's brand tokens (`MAGENTA`, `ORANGE`, `HOT_PINK`, `LEAF`, ...) are re-pointed at gold in Floret
  processes; originals are `OF_<NAME>`.
- Type: General Sans only. Pair Light (300) with Semibold (600) in headlines; small tracked uppercase labels in
  Medium (500). Aliases: `display` 700, `display2`/`head` 600, `ui` 500, `body` 400, `light` 300, `thin` 200.
- Logos: `workspace4/assets/` (logo.png, psx_logo_full.png, pmex_emblem.png). Never recolour or stretch them.
- 3D objects: `kit.obj('logo'|'goldbar'|'silverbar'|'barrel'|'coin'|'shield', t=...)` (Blender renders in
  `workspace4/b3d2`, made by `pipeline/floret/b3d.py`).
- Copy: only claims the client provided (Pakistan's leading brokerage house, 12,000+ active clients
  nationwide, PSX and PMEX access, gold / silver / crude oil, expert insights, built on trust,
  floretcapitals.com). Do not invent figures, prices or returns.
- Currency is the Pakistani rupee: icons `rupee` (Rs) and `coin_rs` (`pound` / `coin` draw them too in Floret
  processes; the toolkit's £ versions are `of_pound` / `of_coin`). `ui.money()` and `T.Counter` default to
  `'Rs '`; `kit.money(12500)` -> `Rs 12,500`. Other icons: `ui.ICONS` (chart, globe, shield, star, bell, ...).

## Look rules (from the client's reference)

Near-black stage, large soft colour blooms behind objects, glossy rim-lit 3D, liquid glass with refraction and
specular rims, clean UI with generous space, slow camera push-ins, letter-by-letter reveals with light sweeps.
Every scene clears before the next enters. Check stills before any full render.

## Data and setup

`workspace*/` is git-ignored. Fonts: `workspace/fonts/GeneralSans-*.ttf` (kit.py downloads them from Fontshare
on first import when missing) and `workspace3/fonts/` (toolkit fonts); `kit.py` links both into
`workspace4/fonts/`. The Floret 3D objects are re-rendered with `pipeline/floret/render_b3d.sh` (~1 h on 4 cores). Python: numpy, opencv-python-headless, pillow, scipy, fonttools, bpy (Blender).
