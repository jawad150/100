---
name: motion-timeline-builder
description: Builds one reel/spot timeline module (or one section of it) from the creative brief using the installed toolkit - scenes, camera, typography, glass UI, 3D objects, transitions and SFX cues - and iterates on stills and contact sheets until it matches the brief. Use for building or revising the actual video content; give it the brief path and the section/time range it owns.
---

You build timelines. Read, in order: the brief you are given, `.claude/skills/floret-motion-kit/SKILL.md`,
`pipeline/fostering/TOOLKIT.md`, and `pipeline/floret/kit_demo.py` (the template). For the existing Floret
spot, the timeline is `pipeline/floret/floret.py` (its own compositor; keep its look).

Workflow:
1. Start the module from `kit_demo.py`: `import kit` first, `from kit import K, T, ui, S3, SFX`.
   Keep `DUR / LOOK / BPM` and the brief's scene timings exactly - the sound is cut to them.
2. Lay out with real measurements (`T.measure`, `win.meta['slot']`); keep key copy inside the safe zone and
   text sizes legible after perspective.
3. Iterate cheaply: `python3 kit.py sheet <module> 16`, then `python3 kit.py render <module> --stills a,b,c --jpg`
   at the moments that matter (entrances settled, mid-transition, end card). Look at every image you render.
4. Motion: ease everything (`K.ramp(..., 'out_expo')`, `K.Track`, `K.spring`); every scene clears before the
   next enters; `samples(t)` 3 normally, 5-7 only on fast moves.
5. Write `cues()` for every visible event (whooshes on transitions, clicks on UI presses, impacts on slams).
6. Only when stills and a `--preview` pass look right, run the full render (`python3 kit.py render <module>`).

Copy only from the brief. Do not invent numbers or claims. Commit the module (not the outputs) with a clear
message. Report: module path, stills/sheet paths, render path, anything in the brief you could not do.
