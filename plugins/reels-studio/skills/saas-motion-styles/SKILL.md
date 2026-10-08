---
description: Recipe book of proven looks and devices for premium 9:16 SaaS-style motion reels made with the reels-studio toolkit. It covers five looks (night neon, amber dashboard, light organic, editorial paper, clean SaaS light), each with palette roles, background, type treatment, 3D and UI devices, transitions, camera, SFX character and when to use it. It also covers device recipes mapped to the exact core / type3d / ui / footage / sprites3d / audio calls - orbit text and tags, glass dock, app-window checklist, card tunnel, counter and slot digits, video-in-type with zoom-through, iris montage hook, light sweep, deep glow, extruded 3D type, and logo end cards with the CTA safe-zone rule.
when_to_use: Use when choosing or briefing a reel's look, when giving each reel in a set a distinct look and device set, or when building or fixing one of these devices in a timeline module.
---

# SaaS motion styles

Pick one look per reel. In a set, no two reels may share a signature device or a transition family, so give each
reel its own look from the list below. Every API call named here is in the project's TOOLKIT.md (toolkit folder
pipeline/<project>/, scaffolded from ${CLAUDE_PLUGIN_ROOT}/toolkit by /reels-studio:new-reel-project). Working
code for each device is in ${CLAUDE_SKILL_DIR}/recipes.md.

**Palette roles, not hex values.** Each look names roles: base, primary glow, secondary/rim, accent, text, and
data/money. Map each role to the client's brand tokens in the brief. Token names in the examples (`'MAGENTA'`,
`'ORANGE'`, `'AMBER'`, `'PLUM'`, `'INK'`, `'IVORY'`) are the toolkit's colour roles. A project re-points them to its
brand in `pipeline/<project>/project.json` `"palette"` and `"font_map"` (read by wsconf.py; see its docstring),
written by reels-studio:brand-kit-builder. Toolkit presets with hard-coded hex (extrude3d/chrome sides, ink_soft,
`K.LOOKS` bloom and black tints, the ui amber tint) need a profile from reels-studio:motion-toolkit-engineer;
BRAND.md lists them. Several widgets also default to the original client's copy (`ui.app_window` title and header,
`ui.button` text, `T.Counter` prefix `£`): always pass those arguments. Never hard-code another client's hex values
or copy in a timeline.

**Rules every look keeps:**
- Key copy inside x 70-1010, y 230-1480. A CTA may reach y 1600. Nothing textual below y 1620, and no copy at
  x > 930 for y 1050-1700.
- No full-frame flash or fade; use local glows, bloom or an exposure push.
- Motion blur never crosses a cut.
- Exits ease out.
- Hook in the first 2-3 s, cut on the beat.

## The five looks

### 1. Night neon
- **Use for:** recruitment and emotional "big question" hooks, launches, dark-mode products, anything that needs
  drama.
- **Palette:**
  - base: a near-black void tinted with the brand's darkest hue;
  - primary glow (dominant, ~60 % of the colour): the brand primary;
  - rim: the brand secondary as a planet-rim or edge light;
  - accent: a hot highlight for glow cores;
  - text: ivory.
- **Background:** `K.background('neon', t, cam, center=(x, y), boost=K.beat_pulse(t, BPM), rim=0|1)`. This gives
  volumetric aurora glows, a lit dot grid and a planet rim. Add dust with `K.Particles(170, seed=7)` and a near
  bokeh layer.
- **Type:**
  - a hero word in `extrude3d` with a gradient face, dark sides and a hot rim;
  - slams in `deep_glow`, with `scrim=0.8` over footage;
  - `neon` tube accents;
  - light sweeps on the hero.
- **3D / UI:**
  - a glass `ui.app_window(look='neon')` with a comet rim (`face_at(sweep=(t * .35) % 1)`);
  - footage in tilted glass cards (`ui.media_face`);
  - night-variant 3D icons;
  - orbit text round a hero object;
  - a glass dock.
- **Transitions:**
  - whip pans (`K.whip_blur`, 5-7 samples);
  - zoom-throughs (`K.zoom_blur`);
  - a light-leak band (`K.light_leak(cv, t, sweep=u)`);
  - an iris ring;
  - an exposure push on cut frames.
- **Camera:** an orbit on an easy ease: `K.Cam.orbit(target, 1650, yaw=K.lerp(8, -4, K.EASE['easy_ease'](u)),
  aperture=34)`. Rack focus along UI rows. Shake on slams: `K.shake(t, 9 * K.impulse(t, t0, 8), 15)`.
- **Footage:** grade with `look='neon'`. On bright full-bleed frames use `K.post(..., footage=1)`.
- **SFX:**
  - heartbeat cold open;
  - flash_hit and whip on montage cuts;
  - impact_big + sub_drop on the question, with a riser ending on the slam;
  - glass_tap, ui_click and check_ding in the UI;
  - logo_sting;
  - bed room_tone or night_air at -30 dB.
- **Watch:** a glow in the logo's own colour swallows the logo. Put a dark pool behind it and use the light-on-dark
  logo variant.

### 2. Amber dashboard
- **Use for:** money, pricing, allowances, ROI, statistics and calculators.
- **Palette:**
  - base: a warm dark;
  - primary glow: amber or gold (dominant);
  - data/money: a gold gradient;
  - brand primary: an accent only (~20 %);
  - text: ivory.
- **Background:** `K.background('amber', t, cam, rim=0)` plus a perspective grid floor,
  `K.grid_floor(cv, cam, y=600, color=K.C['AMBER'], opacity=0.3)`.
- **Type:** `gold` extrusion for titles and totals, and `T.Counter('gold', px=150, prefix=<currency>)` for every
  figure.
- **3D / UI:**
  - a calculator in `ui.app_window(look='amber')`, with `ui.chip` age or plan selectors, `ui.bar_chart(...,
    depth=12)` glossy 3D bars, `ui.slider` and a total line;
  - spinning 3D coins `S3.get('<coin>', 'night', mode='spin')` with spin blur;
  - a `ui.orbit_ring` of glass tags round a 3D object.
- **Transitions:**
  - a card tunnel hook;
  - a coin wiping across the lens;
  - a push or zoom-through into a glowing object;
  - whip pans.
- **Camera:** isometric to front, `K.Cam.orbit(c, 1600, yaw=-19, pitch=11)` easing to yaw 0, pitch 0. Slow
  push-ins on the number.
- **SFX:**
  - coin_flip, coin_ring and coins_burst;
  - cash_kaching when a total lands;
  - `slot_tick`, `slider_drag` and `bar_grow` with `align='start'` at the motion start;
  - whoosh_by in tunnels and orbits;
  - impact_big on the title;
  - bed room_tone at -30 dB.
- **Watch:**
  - Only verified figures, exactly as written.
  - Slot reels must never show a legible fake amount (the default `blur_cap=0.12` keeps streaks).
  - Fine print ≥ 28 px after perspective (30 px on tilted UI).

### 3. Light organic
- **Use for:** brand stories, care, family, wellbeing, sustainability, and daylight warmth.
- **Palette:**
  - base: ivory;
  - blooms: peach, lavender and pink;
  - brand primary and secondary as soft blooms and a closing sunset gradient;
  - accent: leaf green;
  - text: ink.
- **Background:** `K.background('airy', t, cam)` with big drifting bloom billboards (`K.radial`), dappled shadows
  and motes (`K.Particles`, light colours).
- **Type:**
  - `ink_soft` heroes;
  - `glass_pill_light` labels;
  - `T.VideoType(word, look='light')` chapter words with a zoom-through;
  - `ui_ink` below 32 px.
- **3D / UI:**
  - day-variant props: tumbling leaves (`mode='spin'`), a growing sprout (anim), orbs, puzzle pieces;
  - `look='airy'` glass pills;
  - `ui.orbit_ring(look='airy')` with image tags (`F.still(photo, 140, 140, look='airy')` thumbnails).
- **Transitions:**
  - zoom-through a letter stroke or counter (`vt.zoom_point('O', kind='counter')`);
  - an iris growing from an object;
  - a near-lens leaf gust wipe (5 samples);
  - eased dissolves.
- **Camera:** low, close crane-ups, slow drift, airy DOF at aperture 18-34.
- **Footage:** `look='airy'`; inside letters `look='natural'` for contrast.
- **SFX:**
  - seed_plip and ripple;
  - grow_swell (`align='start'`) and leaf_rustle;
  - air_zoom on zoom-throughs;
  - puzzle_click, bubble_pop, pop and shimmer;
  - bed outdoor_birds at -30 dB.
- **Watch:**
  - Pastel blooms must not wash out ink contrast.
  - Bright plates need `K.post(..., footage=1)`.

### 4. Editorial paper
- **Use for:** explainers, "day in the life", lists and routines, pure animation with no footage, and any reel that
  must clearly not look glassy.
- **Palette:**
  - base: cream paper;
  - type: a deep brand dark (plum or ink) plus one brand accent for highlight swipes and brackets;
  - scribbles: secondary accents.
- **Background:** a procedural crumpled-paper sheet relit every frame. It is not in the shared toolkit, so build it
  in `<module>_paper.py`:
  - a multi-scale crease height field becomes normals and an albedo, cached on disk in `<WS>/textures/`;
  - each frame adds a Lambert key, a sky fill and a light pool whose direction and colour follow a time-of-day
    cycle;
  - ink is composited into the albedo before lighting, so type is debossed and lit by the same light.
- **Type:**
  - per-word drops with `T.Glyphs(text, 'flat', font=<display black>, fill=...).slam(...)`;
  - masked line reveals (`rise`, clipped to a slot);
  - "< >" brackets that snap in on `K.spring`;
  - a marker swipe behind a key word;
  - a handwritten accent (`font='hand'` or the brand script) written on, with a scribble underline drawn with
    `ui.stroke_mask([(ui.trim_polyline(pts, 0, u), False)], K.W, K.H, width=7)`, painted with an ink colour.
- **3D / UI:** glossy toy props (day variants) that drop onto the desk with contact and cast shadows following the
  light. Building blocks stack into a tower as a metaphor. No glass cards.
- **Transitions:** a sheet slide (rotation 6° to 0°, edge shadow), a hinged page flip (9-11 samples), and props
  tumbling and morphing into the next idea.
- **Camera:** mostly a locked page. A hook push-in from 1.75x to 1x, with type drawn from 1.75x sprites so it stays
  sharp.
- **SFX:**
  - paper rustle, slide and flip, pencil scribble and prop sounds, synthesised in `<module>_sfx.py` and registered
    into `audio.SOUNDS` at runtime;
  - impact_soft type thumps, ui_tick, pop, and a shimmer at the end;
  - bed room_tone at -32 dB.
- **Watch:**
  - Type must stay pixel-sharp (scale 1, rot 0 snaps to whole px).
  - Light changes must be slow. Never flicker the exposure.

### 5. Clean SaaS light ("follow the object")
- **Use for:** product explainers, "where does the money go", process journeys and B2B SaaS.
- **Palette:**
  - base: true white (linear ~1.16, so it encodes at ~252 and never looks grey);
  - a faint brand-dark dot grid;
  - soft lavender and peach depth glows;
  - one hero stream colour (gold or the brand accent);
  - headlines: ink or brand-dark two-tone;
  - captions: the UI font.
- **Background:** build it in `<module>_fx.py`: a white page, `K.dot_grid(spacing=34, radius=1.6)` alpha on a plane
  behind the stations (so it parallaxes), and far glow billboards.
- **Type:** the hero number in `gold` extrusion with a warm sweep (`sweep_kw=dict(color='AMBER')`); flat display
  headlines.
- **3D / UI:**
  - crisp white glass chips (`ui.chip(..., look='airy')`, `ui.tag(look='airy')`);
  - glossy 3D props with soft tinted drop shadows on the page;
  - a coin or object stream with spin blur;
  - a light-trail ribbon along a Catmull-Rom path through world stations.
- **Transitions:** none. It is one continuous world, and the camera travels between stations; it ends by
  gathering everything into a final object.
- **Camera:**
  - The camera rides the lead object along the path, low-passed, with a pull-back and a bank on moves.
  - Use 6-8 samples on moves (<= ~6 px of camera travel between samples).
  - Held copy rides a separate text camera without the breathing, so it stays pixel-locked.
- **SFX:**
  - coins_burst and coin_ring;
  - whoosh_by on each move, swish_small, pop, glass_tap and ui_click;
  - a soft chime at the end;
  - an airy bed.
- **Watch:**
  - A white light sweep dissolves gold letters into the white page, so sweep with a warm gold band.
  - Use local glows only.
  - Shadows are tinted, not grey.

## Device recipes (code in ${CLAUDE_SKILL_DIR}/recipes.md)
| device | toolkit calls | rules |
|---|---|---|
| Orbit text | `T.OrbitText(text, 'flat', px=56, radius=380, tilt=14, roll=-8, fill='IVORY')`; `ot.draw(cv, cam, c, t=t, part='back')`, then the hero, then `part='front'`; or `ot.add_to_scene(sc, c, t)` | the back half is mirrored, dim and blurred; spin about 20°/s; the ring stays inside x 70-1010 |
| Orbit tags | `ui.orbit_ring(cv, cam, items, phase=t*.05, radius=(rx, rz), tilt, roll, look, mid=draw_hero, enter=[...])`; focus `focus_dist=dist - rz*cos(tilt)` | check every frame: tags readable when parked (give explicit slots if needed), never in the like/share column; each reel in a set gets its own tilt and roll |
| Glass dock | `ui.dock_tile(title, sub, icon, look)`; `ui.dock_face(tile, focus=w, media=clip.get(...), sweep=...)`; `ui.carousel(n, focus, spacing=330, grow=.16)`; `tile.plane(...)` | the focused tile plays footage; a 3D icon lifts above its tile, never over faces; text <= x 915 |
| App-window checklist | `ui.app_window(...)`, `win.face_at(sweep=)`, `ui.check_row(label, w=sw, t=t - tick)`, `win.plane(...)`, `win.screen(...)` + `ui.draw_cursor(press=K.impulse(t, tc, 9), click=t - tc)`, `ui.progress_ring(p)`, `ui.toast(...).plane(...)` | content fits `win.meta['slot']`; ticks on beats; UI text >= 34 px on screen; ui_click + check_ding per tick |
| Card tunnel | `ui.glass_card` + `ui.media_face` (stills, built once); golden-angle helix; camera z surge then exponential brake; `sc.custom(P, card.plane(...))`; depth fog | 0.6-1.0 s, 7 samples; exposure push on the 8ths; whoosh_by on beats, panned |
| Counter / slot digits | `T.Counter('gold', px=150, prefix=...)`; `trk = K.Track([(t0, 0, 'out_expo'), (t1, v)])`; `cnt.draw(cv, trk(t), x, y, vel=trk.vel(t))`; `cnt.slot(...)`; `cnt.sprite(v, vel).draw_plane(cv, cam, P)` | verified figures only; land on a beat; slot_tick `align='start'` with `dur=t1-t0`, cash_kaching or coin_ring at t1 |
| Video-in-type + zoom-through | `T.VideoType(word, px, look)`; `vt.draw(cv, clip.get(t, 1080, 1920, look='natural'), x, y)`; `vt.zoom(u, vt.zoom_point('U'), x, y, s1=46)` then `vt.draw(cv, foot, **z)`; `K.zoom_blur(cv, 0.12*u)` | very heavy letters, high-contrast faces in the letter band; `T.measure` <= 940 px; 7 samples during the zoom; the screen-locked footage lands on the next full-frame shot |
| Iris montage hook | `K.glow(K.ring(300, 4, col), glow_col, (8, 28, 80), 1.3)` built once; a circular mask of radius r(t) (`K.spring` open, `K.ramp` blow-out); `clip.get(..., zoom=1.22->1.0)` per flash | 6-8 flashes on 8ths or triplets; faces centred in the iris; the shot index switches half a frame early; swish + tick per cut |
| Light sweep | `ts.draw(..., sweep=K.ramp(t, t0, t1, 'inout_sine'), sweep_kw=dict(color=..., width=.09, angle=-32))`; `T.light_sweep(ts, u)`; panels `face_at(light=u)`; frame band `K.light_leak(cv, t, sweep=u)` | 0.6-1.0 s per pass; on white looks, a warm band; shimmer SFX |
| Deep glow | `T.render(text, 'deep_glow', px=px, glow_color=(c, 2), scrim=0.8)` or `T.Glyphs(...).slam/rise`; for sprites `K.glow(spr, col, (8, 28, 80), 1.2)` built once | scrim 0.75-0.85 over footage; glow and scrim fade on their own ramps at hand-offs (no pop); the glow colour differs from the logo's colours |
| Extruded 3D type | `T.render(word, 'extrude3d', px=250, fill=(c0, c1, c2), fill_angle=35, depth=.24, angle=-70, persp=.08, side=(...), rim_color=(...))`; `'gold'`, `'chrome'`; `ts.draw_plane(cv, cam, P, rot=...)` for parallax; slam `scale=K.lerp(1.6, 1, K.spring(t-t0, 3.2, .45))` | build in `prewarm()` (0.3-1.2 s); width <= 940 px; impact on the beat, riser ending on it |
| Logo end card | flat `K.load_image(os.path.join(K.BRAND, '<logo>.png'), size=760)` or a 3D mark `S3.get('<mark>', '<variant>_anim').at_time(t - t0)` (last frame == yaw 0); a dark `K.radial` pool behind; `ui.button(cta, hover, press, ripple)` + `ui.draw_cursor('hand')`; particles masked off logo and copy | CTA body inside x 70-1010 with its bottom <= y 1600; any line in y 1050-1700 ends at x <= 930; nothing textual below y 1620; the logo is never recoloured or stretched; the cursor leaves, then the card holds settled >= 1.5 s; logo_sting at the resolve, ui_click + toggle_on on the press |

## Choosing for a set
| reel's job | first choice | second choice |
|---|---|---|
| recruit, provoke, emotional hook | night neon | light organic |
| money, numbers, pricing | amber dashboard | clean SaaS light |
| brand story, values | light organic | editorial paper |
| routine, list, "what it's really like" | editorial paper | clean SaaS light |
| process, journey, "where it goes" | clean SaaS light | amber dashboard |

Write the choice into the brief's look matrix (`reel | look | palette dominance | hero type | signature devices |
transition family | camera | BPM | SFX palette`). Reuse devices from references; never copy their layouts, copy,
footage or audio.
