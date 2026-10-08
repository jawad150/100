---
name: organic-fostering-motion
description: Build, fix, review, render or deliver Organic Fostering motion-graphics videos (reels 1-3, animations anim1 "Day in the Life" and anim4 "£447.60 where does it go", and new pieces) with the toolkit in pipeline/fostering - brand, verified copy, safe zones, module contract, render/package commands, QA rules and workspace recovery.
---

# Organic Fostering motion pieces

**Code:** `pipeline/fostering/` (committed). **Data:** `workspace3/` (git-ignored).
- **Briefs:** `BRIEF.md` (reels 1–3) and `BRIEF2.md` (anim1, anim4).
- **API:** `TOOLKIT.md`.
- **Deliverables:** `reel/organic_fostering/`. Masters are stored with Git LFS.

## Pieces
| module | piece | look | BPM |
|---|---|---|---|
| reel1 | Could You? (26 s) | night neon | 120 |
| reel2 | Financial Support (24 s) | amber dashboard | 128 |
| reel3 | Nurture · Develop · Grow (26 s) | light organic | 92 |
| anim1 | Day in the Life (≈21 s, pure animation) | editorial paper | 100 |
| anim4 | £447.60: where does it go? (≈25 s, pure animation) | clean SaaS light + money stream | 120 |

## Brand and copy
- **Colours:** MAGENTA #B7006E, ORANGE #FF6411, LEAF #64A60B, PLUM #5B174F, INK #321F35, IVORY #FCF8F5, PEACH #FFD4BA.
- **Fonts:** Nunito (display), Poppins (UI), Caveat (handwritten accent).
- **Logos:** `workspace3/brand/`. Use `logo_full.png` on light backgrounds and `logo_full_onDark.png` on dark ones. Never recolour or stretch them.
- **Copy:** only the client's doc or organicfostering.co.uk, exact.
  - Weekly allowance per child: 0–4 £447.60 · 5–10 £473.17 · 11–14 £515.52 · 15+ £554.02. Example: £23,275.20 for 52 weeks.
  - Never use "£2,500" (unit unclear), "24/7" or "guaranteed".
- **CTA:** "Start your enquiry" · 0161 241 1332 · organicfostering.co.uk.
- **Audio:** SFX only. The client adds music.

## Rules that QA enforces
- Key copy inside x 70–1010 and y 230–1480. Never x > 930 for y 1050–1700 (the like/share column). Minimum text: hero 130 px, body 40 px, fine print 28 px.
- No full-frame flash or fade that lifts blacks. No motion-blur samples across cuts. No glow pops at text hand-offs. No camera snaps or one-frame exits. No face crops. No particles on the logo.
- End card settled for at least 1.5 s. SFX at -18 LUFS and ≤ -2 dBTP.

## Commands (run from pipeline/fostering)
```bash
python3 render.py <module> --stills 1,5 --jpg | --sheet 48 | --range a b | --preview   # checks (use --workers 1 while sharing the CPU)
python3 render.py <module> --workers 4        # final master (about 2 GB RAM per worker)
python3 package.py <module> <slug> --cover 1.5  # Instagram mp4 + master + stem + cover -> reel/organic_fostering/
python3 setup_workspace.py [--footage]        # rebuild workspace3 after a container reset
```

## Team
The project agents are in `.claude/agents/`:
- creative-director
- motion-timeline-builder (one per module)
- blender-3d-artist
- sound-designer
- motion-toolkit-engineer
- motion-qa-reviewer (use two lenses, copy/layout and motion/audio, then verify each major finding independently before fixing)

A portable version of the whole team, for other projects, is the reels-studio plugin in `plugins/reels-studio/`. Setting up a local PC is covered in `LOCAL_SETUP.md`.
