# Source and licence

- Upstream: https://github.com/dylantarre/animation-principles (a 144-skill collection on Disney's 12 principles)
- Commit: 8359713 (2025-12-30), cloned depth 1 on 2026-10-08 into
  `workspace/brand_reels/skills/src/dylantarre__animation-principles/` (read only, never executed).
- Licence: MIT, Copyright (c) 2024 Dylan Tarre. Full text in `LICENSE` next to this file.
- Copied verbatim (3 of 144 skills, the ones that apply to video motion graphics):
  - `SKILL.md` <- `skills/01-by-domain/video-motion-graphics/SKILL.md`
  - `references/after-effects.md` <- `skills/09-by-tool-framework/after-effects/SKILL.md`
  - `references/filmmaker.md` <- `skills/03-by-role-persona/filmmaker/SKILL.md`
- The rest of the collection is UI/web oriented (CSS, GSAP, Framer, game dev) and was not installed.

# Translating the After Effects expressions to the Reels Studio toolkit (adaptation, not upstream text)

| AE idiom | toolkit equivalent (pure function of t) |
|---|---|
| overshoot / inertial bounce expression (`amp * sin(t*w) / exp(decay*t)`) | `K.spring(t - t0, freq=2.4, damping=0.42)` (0..1 with overshoot) or the spring-from-contact form `exp(-k*d) * sin(w*d)` after a slam (motion-timeline-builder rule) |
| `valueAtTime(time - delay)` follow-through / stagger by layer index | evaluate the same `K.Track` at `t - i * delay` for element i (keep total stagger <= ~0.5 s or one beat) |
| Easy Ease (F9) | `'easy_ease'` (AE 80/80) for cameras, `'out_cubic'` arrivals, `'in_cubic'` exits |
| `wiggle(freq, amp)` | `K.wiggle(t, freq, amp, seed)` (seeded, deterministic) |
| motion blur switch | `samples(t)` 3 normal, 5-7 on fast moves, never across a hard cut (switch shot half a frame early) |
| 3D layers + camera | `K.Cam` / `K.Cam.orbit` + `K.draw_plane` / `K.Scene` with DOF (`aperture`) |
