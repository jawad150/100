# Bijli series: three new @jawad_mp4 reels (2026-10-11)

Jawad's ask (2026-10-11): "Bijli Chali Gayi" did very well. Make 3 more reels in that spirit: a nostalgic, relatable
desi childhood moment that turns into a video-editor twist, Hinglish / Roman Urdu, 1080x1920, 30 fps, Instagram.

## Hard rules (Jawad)
- **No Jawad face / character-sheet images in the reels.** No `*_faces.py`, no cut-outs, no JD profile shots in the
  story. Every visual is built from **3D Blender elements tied to the concept** (`assets3d_<slug>.py`, bpy 5.2 CPU
  Cycles) composited with the house 2.5D kit (core / jawad_kit / jawad_grade / jawad_tx / type3d / ui / snake_captions).
- **Photoreal 3D (Jawad, 2026-10-11 06:26):** the 3D elements and designs must be realistic renders tied to the content:
  PBR materials with wear (scratches, dust, labels/decals, fingerprints), real-world dimensions, bevels, physically
  plausible lighting (area lights, practicals, warm fill), macro depth of field. Few high-detail hero props in close-up
  beat many simple ones. No stylized blobs or placeholder primitives.
- **Outro = the Genjutsu-style profile outro** of the brand reels: `pipeline/jawad_reels/profile_outro.py`
  (`PO.ProfileOutro(question, dur=4.0)`), each reel with its own question. The small @jawad_mp4 profile-photo badge
  inside that outro stays (it is the outro, not a character sheet).
- Use only the agents / skills / toolkit in this repo (`.claude/agents/*.md`, `plugins/reels-studio`,
  `.claude/skills/{jawad-brand-reels,motion-design,video-motion-graphics,blender-pro-reference}`). Never copy
  Organic Fostering / Floret content, looks or props.
- **Voice:** Bijli used the paid Higgsfield "Vlad" VO. Credits for the new reels are NOT approved yet. Build every reel
  **text-led** (kinetic Hinglish captions carry the story, SFX + original music). Scripts still carry the VO lines
  (Roman + Devanagari) so a VO can be dropped in later if Jawad approves; leave room in the mix for it. Never call any
  paid generation service. Never regenerate the existing paid takes in `brand_reels/assets/*/vo_raw`.

## The three reels
| # | slug | title | moment | editor twist | outro question (draft) |
|---|---|---|---|---|---|
| 1 | `pencil_se_rewind` | Pencil Se Rewind | rewinding a cassette with a pencil, tape ribbon curls, the click | the pencil was our first scrub tool; today we scrub the timeline. Payoff: "Pehla editing tool? Pencil." | Aap ki pehli cassette kaunsi thi? |
| 2 | `thoda_left_bas` | Thoda Left... Bas Bas! | one person on the roof turns the antenna, another shouts "thoda left... bas! ab theek hai!" at a snowy CRT | client feedback on your edit is exactly the same: "thoda left... nahi, pehle wala" | Ghar mein antenna kaun ghumata tha? |
| 3 | `sirf_36_shots` | Sirf 36 Shots | a 36-exposure film roll, every click counted, waiting days for the prints at the studio | today 2 TB of footage and still "ek achha shot nahi hai" | Aap ki pehli camera kaunsi thi? |

## Format (copy from Bijli)
- 30-36 s, 30 fps, a BPM grid (Bijli: 90 BPM, beat 20 f), seamless loop seam back to f0, hook in the first 1.5 s that
  works muted, re-hook near 45 %, payoff near 75 %, profile outro over the last ~4 s.
- House look: dark warm world, flame/amber keyword serif-italic + white grotesk (BRAND.md), jawad_grade looks
  (Bijli used `dusk`). Captions: Roman Urdu, house spelling (bari / bohat).
- Delivery into `reel/jawad_reels/<slug>/` with `pipeline/jawad_reels/tools/deliver_reel.py` conventions: `_ig.mp4`
  (music + SFX), `_ig_songready.mp4` (SFX only, for an in-app song), `_master.mp4`, stems, `_cover.jpg`,
  `_cover_grid_3x4.jpg`, `_caption.txt` (caption, pinned comment, 5 hashtags, "Turn on AI info"), `.srt`, README.md.
  Every file < 95 MB. -14 LUFS, TP <= -1.5 dBTP after AAC (LEAD_DECISIONS).

## Machine
4 cores, 15 GB, shared by parallel agents: every heavy job (Blender, render.py, music render) goes through
`pipeline/jawad_reels/tools/heavy.sh`; render.py with `--workers 1`. Scratch under `workspace/` (git-ignored).
Reference build to copy patterns from: `pipeline/jawad_reels/bijli_chali_gayi*.py`, `assets3d_bijli_chali_gayi.py`,
`brand_reels/design/reels/bijli_chali_gayi/*`, `reel/jawad_reels/bijli_chali_gayi/`.

## Role map (Jawad's named roles -> agent files)
| Jawad's role | agent file(s) |
|---|---|
| content strategist | `.claude/agents/viral-strategist.md`, `trend-researcher.md` |
| script writer | `.claude/agents/hinglish-scriptwriter.md`, `script-hook-writer.md` |
| creative director | `.claude/agents/creative-director.md` |
| UI/UX design | `.claude/agents/caption-designer.md`, `brand-kit-builder.md` (+ `ui.py` glass UI) |
| Blender artist | `.claude/agents/blender-3d-artist.md` |
| sound design | `.claude/agents/sound-designer.md`, `music-supervisor.md` |
| motion designer | `.claude/agents/motion-timeline-builder.md`, `motion-toolkit-engineer.md` |
| QA | `.claude/agents/motion-qa-reviewer.md` |
