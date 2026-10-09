# Working rules for this repository

## Model and effort policy (set by the repository owner)
All work runs on **Opus 5.5** (`claude-opus-5-5`), set in `.claude/settings.json` and in every agent's frontmatter.
Effort is matched to the task:

| Task | How it runs |
|---|---|
| **Routine / low-effort**: questions, status and time estimates, small edits, file moves, packaging, re-muxes, commits and pushes | The session default, **medium** effort (`effortLevel` in `.claude/settings.json`) |
| **High-priority**: client deliverables, timeline and toolkit changes, renders, QA reviews, fixes found by QA, audio mixes | **High** effort: the agents that own this work (`motion-qa-reviewer`, `motion-timeline-builder`, `motion-toolkit-engineer`, `creative-director`, `blender-3d-artist`, `sound-designer`, and the reels-studio builders, QA, music supervisor, footage editor and script writer) run with `effort: high` in their frontmatter. Research, reference, brand-kit, caption and packaging agents run at `effort: medium` |
| **Complex, multi-step**: new reels or sets of reels, multi-piece builds, audits, anything that needs parallel agents and independent verification | **Ultracode**: run it as a multi-agent workflow (Workflow tool) that plans, builds in parallel, verifies adversarially and fixes. In workflow scripts pass `effort: 'medium'` to mechanical stages (listing, packaging, measuring) and `effort: 'high'` to builders, reviewers and verifiers |

The owner can force ultracode for any request by including the word "ultracode" in the prompt.
