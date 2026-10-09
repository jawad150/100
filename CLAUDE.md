# Working rules for this repository

## Model and effort policy (set by the repository owner)
All work runs on **Opus 5.5** (`claude-opus-5-5`), set in `.claude/settings.json` and in every agent's frontmatter.
Effort is matched to the size of the task:

| Task | Effort |
|---|---|
| **Small tasks**: questions, status and time estimates, small edits, file moves, re-muxes, commits and pushes | **Low or medium.** The session default is `medium` (`effortLevel` in `.claude/settings.json`); purely mechanical steps (listing files, copying, measuring, packaging) run at `low` |
| **Complex tasks**: client deliverables, new or changed timelines and toolkit code, renders, audio composition and mixes, fixes found by QA | **High or max.** Builder agents run with `effort: high` in their frontmatter (`motion-timeline-builder`, `motion-toolkit-engineer`, `creative-director`, `blender-3d-artist`, `sound-designer`, and the reels-studio builders, music supervisor, footage editor and script writer). QA and verification run at `effort: max` (`motion-qa-reviewer`). Research, reference, brand-kit, caption and packaging agents run at `effort: medium` |
| **Complex, multi-step tasks**: new reels or sets of reels, multi-piece builds, audits, anything that needs parallel agents and independent verification | **Ultracode**: run it as a multi-agent workflow (Workflow tool) that plans, builds in parallel, verifies adversarially and fixes. In workflow scripts pass `effort: 'low'` to mechanical stages (listing, packaging, measuring), `effort: 'high'` to builders and fixers, and `effort: 'max'` to reviewers, verifiers and judges |

The owner can force ultracode for any request by including the word "ultracode" in the prompt.
