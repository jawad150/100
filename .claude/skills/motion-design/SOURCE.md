# Source and licence

- Upstream: https://github.com/LottieFiles/motion-design-skill (path `skills/motion-design/`)
- Commit: f9a8a04 (2026-05-18), cloned depth 1 on 2026-10-08 into
  `workspace/brand_reels/skills/src/LottieFiles__motion-design-skill/` (read only, never executed).
- Licence: MIT, Copyright (c) 2025 LottieFiles. Full text in `LICENSE` next to this file.
- Copied verbatim: `SKILL.md`, `director/`, `patterns/`, `reference/` (markdown only; the skill has no scripts, no
  network calls, no API keys).

# How to use it on the Jawad reels (adaptation, not upstream text)

The upstream tables are written for UI motion in milliseconds. For 9:16 reels on the Reels Studio toolkit:
- Convert ms to frames at 30 fps (33.3 ms per frame) and then snap to the brief's BPM grid
  (`K.beat(n, BPM)`): a "card enter 200-350 ms" becomes 6-10 frames, landing on a beat or an 8th.
- Map easing names to toolkit eases: ease-out-cubic -> `'out_cubic'`, ease-out-expo -> `'out_expo'`,
  ease-out-back -> `'out_back'` or `K.spring(t - t0, freq, damping)`, sine in-out -> `'inout_sine'`,
  AE "easy ease" -> `'easy_ease'`, arbitrary cubic-bezier -> `K.bezier(x1, y1, x2, y2)`.
- Personality for @jawad_mp4: "Energetic" for hooks and slams, "Premium" for the serif-italic keyword reveals,
  never "Playful" bounce on brand type.
- The toolkit rules still win where they are stricter: always pass an ease to `K.ramp` (its default
  `'out_expo'` front-loads 60 % of a fade into 1-2 frames), exits ease out over >= 0.2 s, no full-frame flash.
