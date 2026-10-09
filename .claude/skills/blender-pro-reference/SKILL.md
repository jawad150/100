---
name: blender-pro-reference
description: Reference notes for writing headless Blender 5.2 bpy scripts - three-point / studio / low-key lighting ratios and recipes, colour temperature table, Geometry Nodes built from Python (scatter, instances, curves, fields, Scene Time animation), Cycles sampling and denoising, cameras, focal lengths, DOF and composition, Principled BSDF materials. Use alongside the reels-studio blender-3d-artist when building new props, product-style hero renders or procedural (Geometry Nodes) elements for a reel, or when a render looks flat, noisy or badly lit.
---

# Blender pro reference (headless bpy, no MCP)

Reference-only skill. The five files in `references/` are copied verbatim from RobLe3/cc-blender-skill
(MIT, see `LICENSE` and `SOURCE.md`). Upstream wrote them for a live Blender session driven over the BlenderMCP
socket; here nothing connects to a live Blender. Every snippet runs as plain `bpy` (Blender 5.2 is installed as a
Python module: `python3 -c "import bpy; print(bpy.app.version_string)"`), CPU only, inside the
reels-studio builder pattern (`assets3d_<set>.py`, `H.reset(...)`, `write_meta` last).

| file | read it for |
|---|---|
| `references/lighting.md` | key:fill:rim ratios (high-key 2:1, portrait 4:1, low-key 8:1, rim 0.5-1x key), studio product and noir recipes, colour temperatures, soft vs hard shadows, pitfalls |
| `references/geometry-nodes.md` | building a GN tree from Python (`node_group.interface.new_socket`, node idnames), scatter / instance / curve recipes, fields, Scene Time animation, realize before export |
| `references/rendering.md` | Cycles sampling, adaptive threshold, OIDN, light paths, persistent data, colour management |
| `references/cameras-composition.md` | focal length cheat sheet, DOF, hero-shot camera, orbit/dolly/push-in rigs, composition rules |
| `references/materials-shading.md` | Principled BSDF recipes (glass, metal, plastic, emission), node wiring |

## Errata for Blender 5.2.2 (checked on this machine on 2026-10-08)
- Noise Texture output is named `'Factor'`, not `'Fac'` (`noise.outputs['Factor']`). Offsetting positions with it
  needs a `ShaderNodeCombineXYZ` (the upstream snippet says so in a comment but wires `Fac` directly).
- `scene.cycles.denoising_use_animation` does not exist. What exists: `use_denoising`, `denoiser`
  (`'OPENIMAGEDENOISE'` on CPU), `denoising_input_passes = 'RGB_ALBEDO_NORMAL'`, `denoising_prefilter`,
  `use_adaptive_sampling`, `adaptive_threshold`, `adaptive_min_samples`, `use_light_tree`, `seed`,
  `use_animated_seed`. Against boiling noise in sequences keep `use_animated_seed = False` and a fixed `seed`
  (reels-studio asset spec).
- Device: `scene.cycles.device` is `'CPU'` here (no GPU; CUDA init fails harmlessly). Use
  `sc.render.threads_mode = 'FIXED'`, `sc.render.threads = 2` and `nice -n 10` (shared machine).
- Colour management defaults to `'AgX'` in 5.2. The reels-studio sprite spec needs `view_transform = 'Standard'`,
  `look = 'None'`. `I.reset(...)` / `H.reset(...)` in the toolkit builders already set it; a custom reset or a
  snippet pasted from `references/` must set it too, or sprites come out with AgX's compressed, desaturated
  highlights.
- `Material.use_nodes` is deprecated (removal planned for 6.0); new materials already have a `node_tree`.
  Principled BSDF socket names in 5.2 include `'Base Color'`, `'Roughness'`, `'Coat Weight'`, `'Coat Roughness'`,
  `'Transmission Weight'`, `'Emission Color'`, `'Emission Strength'`, `'Thin Film Thickness'`.
- Light datablocks: AREA has `size`, `size_y`, `shape`, `spread`; SPOT has `spot_size`, `spot_blend`; SUN has
  `angle`; all have `energy` and `shadow_soft_size`.
- Upstream mentions Poly Haven HDRIs (CC0). Downloading one is fine (new folder, untrusted data), but the
  reels-studio look standard prefers emissive cards over HDRIs so reflections stay controlled and on-brand.

## House rules that override the references for @jawad_mp4 work
- Brand light: red-orange rims and warm keys on near-black worlds (see the `jawad-brand-reels` skill), not the
  upstream "warm key / cool blue rim" Hollywood default. A cool fill is allowed only as a faint separator.
- Never reuse the toolkit's earlier-client props (house, heart, coin_gbp, pound_glyph, sprout, leaf, seed,
  puzzle_pair, blocks, logo_mark3d, star_badge, shield_check ...). Build new props in a new builder.
