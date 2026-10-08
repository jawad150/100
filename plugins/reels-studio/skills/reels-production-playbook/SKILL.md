---
description: How the main session runs a 9:16 motion-graphics reel project end to end with the reels-studio agent team. The stages are intake, the creative-director brief, parallel 3D asset and timeline builds on placeholders, sound and music, a full-quality render by the lead, two-lens QA with an independent verifier per major finding, fixes by the original builder, a re-render and delivery. It also covers CPU and RAM budgets (4-core cloud versus a 24-core 16 GB PC), file ownership, status updates, measured stage times, container-reset recovery, git hygiene when other sessions share the branch, and the full production-lessons checklist. Bundles qa_measure.py (objective QA measurements).
when_to_use: Use at the start of any reel or motion-graphics project, when planning, resuming or recovering one, when deciding which agent runs next or how many can run at once, and before rendering, QA or delivery.
---

# Reels production playbook

You, the main session, are the producer. You run intake, delegate each stage to a reels-studio agent, own the
render queue and git merges, and keep the user informed. Agents work only in the files they own. Prompts for every
delegation, measured timings and recovery details are in ${CLAUDE_SKILL_DIR}/reference.md.
`${CLAUDE_SKILL_DIR}/qa_measure.py` (probe, sheets, strips, luma, snaps, roi, freeze, guides, ink, cues, audio)
is the measuring tool for QA and delivery.

## Team
| agent (`reels-studio:<name>`) | stage | owns |
|---|---|---|
| creative-director | brief, re-plans | `pipeline/<project>/BRIEF.md` |
| reference-analyst, trend-researcher | intake research | their reports |
| script-hook-writer | hooks and on-screen lines from the copy table | the copy section it is given |
| footage-editor | clip moments, crop centres, ramps, grades | shot tables (in the brief or module) |
| blender-3d-artist | 3D props, logo marks, glyphs | `assets3d_*.py` builders, `<WS>/assets3d/<name>/` |
| motion-timeline-builder (one per reel or section) | timelines | `<module>.py`, `<module>_fx.py`, `<module>_dev.py` |
| motion-toolkit-engineer | toolkit features, brand kit profile | the toolkit modules, `<brand>_kit.py` |
| sound-designer | SFX cues, custom sounds, mix, stem | `<module>_sfx.py`, `<WS>/audio/<module>_*` |
| music-supervisor | music on the BPM grid, licence, music mix | music files and its mix notes |
| motion-qa-reviewer | lens A, lens B, verify mode | `<WS>/out/<module>/qa/` only |
| delivery-packager | exports, LFS commit, push | the delivery folder |

Skills: /reels-studio:new-reel-project scaffolds pipeline/<project>/ from ${CLAUDE_PLUGIN_ROOT}/toolkit, and
/reels-studio:saas-motion-styles is the look and device recipe book.

## Stages
1. **Intake (you).** Collect:
   - the client doc (Google Doc: `curl -sL "https://docs.google.com/document/d/<ID>/export?format=txt"`);
   - the website URL, footage link, logo and brand files, and reference reels;
   - platforms, the number of reels, durations, deadline, and audio policy (SFX only or with music; licence);
   - whether the reels run as paid ads (stricter safe zone).
   Ask once, as one consolidated list. Scaffold with /reels-studio:new-reel-project. Footage goes to the
   workspace (pre-extracted frames).
2. **Brief.** Run reference-analyst (and trend-researcher, if useful) first, in parallel. creative-director then
   writes BRIEF.md: deliverables, brand tokens, the verified-copy table, a per-scene timeline on a BPM grid, the
   look matrix (a distinct look and device set per reel), the SFX plan and the module contract. script-hook-writer
   writes hooks and lines from the copy table. **Gate:** the user approves the copy, figures, looks and hooks.
   Ambiguous figures stay out until the client answers.
3. **Builds, in parallel.**
   - A new brand gets its kit profile from motion-toolkit-engineer before the builders start.
   - blender-3d-artist renders the brief's assets list. footage-editor picks moments and crops for footage shots.
   - One motion-timeline-builder per reel (per section for reels over ~30 s, with one named dispatcher owner) starts
     at once on labelled placeholders. They switch automatically when `<WS>/assets3d/<name>/<variant>/meta.json`
     appears.
   - Builders iterate with sheets, stills, range renders and previews at `--workers 1`.
4. **Sound.** Once a reel's events are locked, sound-designer builds its cues and mix, and music-supervisor (if there
   is music) delivers music on the BPM grid.
   - Targets: SFX only, -18 LUFS; with music, about -14 LUFS; ≤ -2.0 dBTP either way.
   - A custom mix must not be overwritten by render.py's automatic rebuild (`--no-sfx-build`, or `--audio <wav>`).
   - Sound can start from the shot list while timelines are polished.
5. **Full-quality render (you, sequential).** One reel at a time, in the background:
   `nice -n 10 python3 render.py <module> --workers <N>`, with N from the budget table. Check
   `render_stats.json` (s/frame, `worker_max_rss_mb`) and Read a few frames before QA.
6. **QA.**
   - Run two motion-qa-reviewer instances in parallel per reel: lens A (copy, layout, legibility, safe zones) and
     lens B (motion, transitions, finish, audio sync).
   - Merge their tables, removing duplicates.
   - Send every blocker and major to a fresh motion-qa-reviewer in verify mode, all in parallel. Only CONFIRMED or
     PARTLY findings go to fixing.
7. **Fixes.** Each confirmed finding goes to the owner of the file (builder, sound, 3D, toolkit), never to whoever is
   free. Owners prove each fix with range renders across the affected time ±0.4 s plus the measurement that
   failed.
8. **Re-render** the full master (stage 5). A regression QA pass then re-measures the fixed ranges, runs `probe`
   and `audio`, and checks a fresh 5 fps sheet. Repeat stages 6-8 until there are no blockers or majors.
9. **Delivery.** delivery-packager makes the exports, verifies them with ffprobe, and commits with LFS, fetch, merge
   and push. Send the user the preview, the deliverables table and the cover.

## Parallelism and CPU/RAM budget
Each render worker holds its own caches and uses about 2 GB. `draw(t)` must stay pure, with static sprites cached.

| | 4-core cloud container (~14 GB limit) | i9 PC, 24 cores / 32 threads, 16 GB, WSL2 |
|---|---|---|
| full render | 4 workers, alone, under `nice` | 4 workers (RAM-bound, not core-bound); 3 if WSL has its default 8 GB |
| builder iteration | `--workers 1`, at most 2-3 builders rendering at once | `--workers 1-2`, up to 4 builders |
| Blender | threads 2 under `nice`; ~1.5 h per 1,000 frames | GPU (RTX 4060) if the builder supports it; 10-15 min per 1,000 frames |
| during a full render | agents write code only; no other renders | light work only (sheets, QA decoding) |

- Check memory before launching: `free -g` (WSL: set `memory=12GB` in `%UserProfile%\.wslconfig`, then run
  `wsl --shutdown`).
- render.py retries with one worker fewer if a worker is OOM-killed. Treat that as a signal to lower N.
- Run heavy jobs with `nice -n 10`.
- Wait loops use bracketed patterns, `pgrep -f "render[.]py <module>"`, because an unbracketed pattern matches the
  pgrep command line itself.

## Ownership rules
- One owner per file. The shared toolkit (core, type3d, ui, footage, sprites3d, audio, render, package,
  setup_workspace) is read-only for builders. Changes go through motion-toolkit-engineer, and bugs are reported,
  not patched.
- `cues()` lives in the timeline module, which the builder owns. If the sound designer must change cue lists,
  make `cues()` a one-line delegate to `<module>_sfx.cues()`, so each file still has one owner.
- Change the brief only through creative-director. Mark the change and tell every affected owner.
- QA never edits. Builders never run full masters; the lead owns the render queue.
- When a fix spans two owners, split it, and say who goes first.
- Agents commit only the paths they own (`git add <paths>`, never `git add -A`).

## Status updates to the user
Post at every gate and about every 30 minutes during long stages. Keep each update to four or five lines:
- what finished (with one image: a sheet, still or cover);
- what is running, with an ETA from render progress lines;
- what is next;
- decisions needed (copy, figures, looks, licences).
Never present unverified copy as final. Say plainly when a stage slips and why.

## Measured stage times (one 3-reel set and 2 pure animations, cloud, 4 cores)
| stage | cloud | PC (est.) |
|---|---|---|
| brief with copy table and looks | 30-60 min | same |
| 3D props, ~1,000 frames | ~1.5 h | 10-15 min on GPU |
| timeline, first complete pass, footage reel | 1-1.5 h per reel (3 in parallel) | same (agent-bound) |
| timeline, custom-look animation (paper, journey) | 3-4 h per piece | same |
| contact sheet / preview (15 fps, 1 sample) | ~1 min / 3-6 min | faster |
| full master, 26 s (1.3-4 s per frame per worker) | 13-15 min | 4-6 min at 4 workers |
| encodes and packaging | ~5 min | 1-2 min |
| QA (two lenses + verifiers) and fixes | ~1.3 h for 3 reels in parallel | same |
| re-render, per reel, sequential | 13-15 min | 4-6 min |
For a new set with the toolkit ready, plan about 4-5 h in the cloud from approved brief to delivery.

## Container reset and recovery
Cloud containers reset. Git-ignored workspace data and running jobs are lost; only pushed commits survive.
1. `git status`, `git fetch origin && git merge --no-edit origin/<branch>`.
2. In the toolkit folder: `python3 setup_workspace.py [--footage]` rebuilds fonts, brand files, site photos and
   footage frames.
3. 3D: `git lfs pull --include="media/<project>/*"` then `tar -xf media/<project>/assets3d.tar -C <WS>`, or
   re-render with the builders. After every set of final 3D renders, archive them:
   `tar -cf media/<project>/assets3d.tar -C <WS> assets3d`, `git lfs track "media/<project>/*.tar"`, commit and
   push.
4. SFX mixes rebuild from `cues()` (or the sound designer's build command). Re-run renders that were in flight.
5. Make a sheet per module to confirm the state before continuing.

## Git hygiene
- Commit and push early and often: after the brief, after each agent hand-back, and after each render or fix round.
- Other sessions may push to the same branch. Before every push, `git fetch` and merge, resolving conflicts by
  keeping both sides' intent. Never force-push, and never rebase published commits.
- Masters and tarballs go in Git LFS. Never commit the workspace.
- Open a PR only when the user asks.

## Lessons checklist (verify each before delivery)
- [ ] **Brief first:** one brief with deliverables, brand tokens, verified copy only (no invented stats, prices or
      claims; ambiguous figures asked about), a BPM-grid timeline, per-scene looks, an SFX plan and the module
      contract. Each reel in a set has its own look and devices.
- [ ] **Safe zones at 1080x1920:** key copy inside x 70-1010, y 230-1480; a CTA may reach y 1600; no copy at x > 930
      for y 1050-1700; the bottom 300 px clear.
- [ ] **Sizes:** hero ≥ 130 px, UI body ≥ 34-40 px, fine print ≥ 28 px.
- [ ] **No full-frame flash or fade that lifts the blacks.** Use local glows, bloom on bright areas or an exposure
      push. Proof: YMIN does not jump (signalstats).
- [ ] **Motion-blur samples never cross a hard cut.** Switch the shot half a frame early.
- [ ] **Text hand-offs are continuous:** glow and scrim fade on their own ramps.
- [ ] **Camera tracks have no discontinuities.** Check every frame around moves (a 1-frame 136 px snap shipped
      once).
- [ ] **Faces are framed deliberately.** No eye or face cut at a frame or card edge; no 3D icon over a face.
- [ ] **Fast moves use 5-7 samples;** spinning objects get directional or spin blur.
- [ ] **No one-frame jump-cut exits.** Ease them out.
- [ ] **Contrast:** no logo glow in the logo's own colours; no particles or bokeh on the logo, wordmark or copy.
- [ ] **Performance:** ≤ 4 workers on 16 GB; `draw(t)` pure with no per-frame state or cycles; `nice`; Blender
      threads 2 when sharing; static sprites cached.
- [ ] **Ops:** push early; setup_workspace.py plus the LFS 3D archive restore a reset container; fetch and merge,
      never force; bracketed pgrep patterns.
- [ ] **Audio, measured not heard:**
      - LUFS, true peak, spectrogram, and cue times checked against frames;
      - -18 LUFS SFX-only, about -14 LUFS with music, mix ≤ -2.0 dBTP;
      - `align='hit'`; at most ~3 sounds per instant;
      - music on the BPM grid.
- [ ] **QA:**
      - two lenses, plus a skeptical verifier per major finding;
      - 5 fps sheets plus every frame within ±0.4 s of each transition;
      - pixel extents, signalstats and ebur128 measured.
- [ ] **Delivery:**
      - H.264 High, 2-pass ~22 Mbps (< 100 MB for 26 s), +faststart, AAC 320k;
      - a CRF 14 master in LFS;
      - a 48 kHz 24-bit stem and a cover JPG;
      - a preview at ~7 Mbps (< 30 MB);
      - ffprobe checks of duration, fps and frame count.
- [ ] **Footage:**
      - frames pre-extracted; 4K scaled to 1920 tall; 1080p sources not zoomed beyond ~1.3x;
      - time remaps frame-blended (25 to 30 fps);
      - skin natural;
      - video-in-type only with high-contrast faces and very heavy letters, then a zoom through.
- [ ] **Hook:** the first 2-3 s stop the scroll (fast montage, a bold question or number, a slam), cut on the beat.
