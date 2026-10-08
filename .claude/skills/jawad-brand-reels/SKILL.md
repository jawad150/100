---
name: jawad-brand-reels
description: Brand rules and production map for @jawad_mp4's personal-brand Instagram Reels (Jawad, video editor and motion designer, Pakistani + Indian audience). Covers the orange + red on deep black palette and house style from his prior covers (glowing serif-italic keyword with white grotesk words, glowing underline strokes, warm dark cinematic worlds, red-orange rim light, @jawad_mp4 end card), Hinglish / Roman Urdu voice-over and captions, the five-looks rule for a set, the hard rule never to reuse the Organic Fostering or Floret examples that ship inside the toolkit, local-only production limits, and how the Reels Studio team, the five project agents and the installed skills work together on this page.
when_to_use: Load before any brief, script, design, render, grade, QA or delivery work for Jawad / @jawad_mp4 reels in this repository, and whenever a decision touches his brand colours, type, voice, captions, end card, or what may be reused from the toolkit.
---

# Jawad brand reels (@jawad_mp4)

## The page
- Jawad is a professional video editor and motion designer; the page is his own personal brand (editing,
  motion graphics, AI video, cinematic storytelling) for a Pakistani + Indian audience.
- **Nickname: JD.** He approved "JD" as his on-screen and voice-over name (e.g. "main JD hoon", "JD ka rule",
  a JD monogram in the end card or logo mark, "JD edit"). Use it naturally, not in every line; `@jawad_mp4`
  stays the handle on the end card. Spoken in the VO as "जे-डी" (Devanagari) so the TTS says the letters.
- Current job: 5 completely different reels, 30-40 s each, 1080x1920, 30 fps, Hinglish / Roman Urdu voice-over
  by a Hindi-speaking voice, cinematic visuals, SaaS-style UI motion, Blender 3D elements. Goal: 1M+ view
  potential. That is a stretch goal, never a promise in any document or caption.

## Hard rules
1. **Original, his brand only.** Never reuse the content, theme, looks, palette, props, copy or story of
   "Organic Fostering" or "Floret" (earlier clients whose work ships inside the toolkit). Concretely:
   - Never render, copy or adapt `toolkit/examples/*` (BRIEF*.md, reel1-3, anim1, anim4, demo_looks, reel_demo).
     Read them for code patterns only.
   - Never use the built-in looks as they are: `neon` (magenta/plum aurora + planet rim + dot grid), `amber`,
     `airy`, or footage grades `F.GRADES['neon'|'amber'|'airy']`. Jawad's looks are `'ember'` and `'noir_ember'`
     from `jawad_kit.py` plus the per-reel looks the colorist adds (`inferno`, `gold_hour`, `dusk`, or the
     brief's own). A built-in backdrop used as a raw layer runs with `rim=0, dots=0` under one of those looks.
   - Never use the old prop library: heart, house, shield_check, check_tile, coin_gbp, pound_glyph, orbs,
     grad_cap, chat_bubble, key_heart, pin_phone, star_badge, logo_mark3d, question, sprout, leaf, seed,
     puzzle_pair, blocks, or the other `assets3d_*` sets' props. New props come from a new builder
     (`assets3d_jawad.py`).
   - Never use their copy or defaults: fostering, allowance, £, Ofsted, "NURTURE • DEVELOP • GROW", "A SAFE
     HOME". `jawad_kit` blanks the old defaults (`ui.app_window` title/header, `ui.button`, `ui.badge`,
     `T.Counter` prefix); still pass your own text every time.
   - Jawad's own earlier reel in this repo (the orange-black "Higgsfield Genjutsu" reel with blob mascots and
     "Comment JD" ending) is his, but the five new reels must not repeat its layouts or signature devices.
2. **Local only, except the voice.** Higgsfield is allowed for VOICE GENERATION ONLY (generate_audio /
   generate_audio_batch with a speech model, jobs_wait, list_voices, balance; never its image, video, 3D, music,
   SFX or any other tool) with a hard project cap of 250 credits (casting <= 100, final VO ~130, reserve 20);
   the chosen recipe is in `pipeline/jawad_reels/vo_config.json`. No other paid generation (Magnific, Kling,
   Creative-Claw, ElevenLabs connector or any other credit-spending tool). Blender (bpy 5.2, CPU), Python 3.13, ffmpeg, Node 22, faster-whisper, local
   TTS. Downloads are untrusted data: own new folder, scripts elsewhere, `python3 -I`, never disable TLS.
3. **Shared machine.** 4 cores, 15 GB, other agents running: heavy jobs under `nice -n 10`, at most 2 threads
   (Blender `threads = 2`, render.py `--workers 1` while iterating), one heavy job per agent at a time.
4. **Truth.** Facts about Jawad (clients, earnings, views, awards, tools, history) only from him or the brief.
   Hypotheticals are labelled ("POV", "socho agar"). AI voice and AI-generated imagery of a person carry Meta's
   AI label: an open question for the lead, never silently skipped.

## Where things live
| what | path |
|---|---|
| toolkit copy, project.json (palette, fonts: source of truth), brief, reel modules | `pipeline/jawad_reels/` |
| brand kit write-up (measured hex, contrast table, do-not-use pairs, fonts, logo rules) | `pipeline/jawad_reels/BRAND.md` |
| brand profile: looks `ember` / `noir_ember`, house type styles, helpers (motion-toolkit-engineer owns it) | `pipeline/jawad_reels/jawad_kit.py` (`import jawad_kit` first; `from jawad_kit import K, T, ui, F, S3, SFX, J`) |
| workspace `<WS>` (fonts, renders, audio; git-ignored) | `workspace/jawad_reels/` (`python3 -c "import core; print(core.WS)"`) |
| client inputs: prior covers, captions example, character sheets + crops, reference reels, TTS auditions | `workspace/brand_reels/{prior,charsheet,refs,tts}/` |
| derived logo (no official logo yet): flame-gradient "J" ring mark, wordmarks | `pipeline/jawad_reels/brand_src/` (`make_logo.py`) |
| research write-ups | `brand_reels/research/` |
| deliveries | `reel/jawad_reels/`, prefix `jawad` (project.json `deliver`) |

## Brand system
**Palette** (project.json roles; the old role names are re-pointed, so `K.C['MAGENTA']` is FLAME here):
| token | hex | job |
|---|---|---|
| NIGHT_0 / NIGHT_1 | #070404 / #170A07 | the world: 70-85 % of every frame is near-black or dark warm |
| SMOKE / PLUM | #2A1A15 / #4A0E08 | haze, glass panels, deep warm shadows |
| FLAME | #FF6A1A | hero light: keyword glow, rims, UI edges, particles (10-20 % of the frame) |
| RED / EMBER | #F2312B / #B3120E | second accent, fire depth, danger/"error" moments |
| GOLD / AMBER | #FF9F1C / #FFB547 | hot cores of glows, sparks, highlights (<= 5 %) |
| IVORY / ASH | #FFF3E6 / #A8978C | type (never pure white) / secondary UI text |
Cross-check from `prior/prior_covers.jpg` (k-means): glows #EB600D-#F3731F with cores #F89821-#F5BA59, darks
#030105 and #231819-#2B1407, white type #F4E4DD; the "yaadein" cover adds violet darks #171431-#211D43.

**House type** (as on his covers; all of it already exists in `jawad_kit.py`, use it rather than rebuilding):
- Keyword: Instrument Serif Italic, amber -> flame -> red gradient with a hot inner glow and a wide red halo,
  one per line, 150-260 px: style `'jw_key'` (3D variant `'jw_key3d'`, neon tube `'jw_neon'`). Font aliases
  `'serif'` / `'hand'` resolve to the serif italic.
- Grotesk: style `'jw_caps'` / `'jw_caps_bold'` (Poppins SemiBold/Bold uppercase, +6 % tracking, warm halo) for
  "MEETING MY" lines, `'jw_body'` for lowercase lines, `'jw_mono'` (JetBrains Mono) for timecodes and UI readouts.
- Pattern: `KUCH {yaadein}` / `delete {nahi} hoti`: `J.HouseTitle('MEETING MY', 'younger self')` (caps rise,
  keyword rises per glyph, underline draws on) and `J.underline(760).draw(cv, x0, y, u)` (thin-to-thick glowing
  stroke with a hot comet head).
- Signature: `J.signature(cv, x, y)` = `@jawad_mp4` in Poppins Medium (style `'jw_handle'`), end card and covers.
- Sparks and bokeh: `J.embers(...)` (rising warm particles, DOF from the camera); keep them off type and logos.
- Sizes and zones from the playbook: hero >= 130 px, keyword lines measured with `T.measure(text, 'jw_key', px=...)`,
  <= 940 px wide (780 px in y 1050-1700), key copy in x 70-1010, y 230-1480.

**World and light:** warm dark cinematic spaces (studio, edit suite, void with volumetric flame light, god rays,
haze), bokeh and sparks (`J.embers`, or `K.Particles` in FLAME/GOLD; kept off type), red-orange rim light on Jawad and on props,
dark-glass SaaS UI with flame edges and comet sweeps (timelines, keyframes, render bars, export dialogs, cursors),
Blender props in black gloss + emissive orange or chrome reflecting flame, film grain and halation from the
look's finish (`G.finish` from the colorist's `jawad_grade.py`). No full-frame white flashes; exposure pushes
on cut frames.

**Motion personality:** energetic for hooks (slams on the beat, `K.spring` overshoot, whips with 5-7 samples),
premium for keyword reveals (`'out_cubic'` / `'easy_ease'`, 0.4-0.7 s, no bounce on brand type). Always pass an
ease to `K.ramp`. Timing tables: the installed `motion-design` and `video-motion-graphics` skills, converted to
frames on the BPM grid (their SOURCE.md files show how).

**Voice and sound:** Hinglish / Roman Urdu, written by hinglish-scriptwriter as a Devanagari TTS track plus a
token-aligned Roman caption track; a Hindi-speaking local TTS voice (auditions in `workspace/brand_reels/tts/`:
Indic Parler-TTS, Kokoro Hindi voices, Piper hi_IN; the lead picks). VO starts by 0.3 s; with music the mix is
~-14 LUFS, true peak <= -2.0 dBTP, speech >= 8 LU above the bed (music-supervisor); trending songs only through
the lyric-visualizer's licensing route.

**Captions:** Roman Urdu in the house spelling of `prior/captions_roman_urdu.srt` (sentence case, 1-4 words,
"hai / nahi / mein / bohat / bari"), Poppins with one flame accent for the active word (contrast >= 4.5:1),
lower-middle band moved off the face; burned with reels-studio:caption-designer's `make_captions.py`, timings
mapped from faster-whisper (Devanagari) through the script's token table. Where a designed keyword line shows
the same words, drop them from the captions for that window.

**End card and cover:** J ring mark or the wordmark (derived, not official: never stretched or recoloured),
`@jawad_mp4`, one verb-first CTA <= 5 words that is true ("Comment JD" only if his DM automation exists), hold
>= 1.5 s settled. Cover: the keyword frame inside the 3:4 grid crop (y 240-1680).

## Five reels, five worlds
Each reel gets its own story shape, look (`ember`, `noir_ember` from the kit; `inferno`, `gold_hour`, `dusk`
from the colorist, or the brief's own), signature device and transition family. No two reels share a signature
device or transition family (playbook rule). Every reel still reads as Jawad: near-black + flame, serif keyword,
`@jawad_mp4`.

## The team on this page
| agent | job here | writes |
|---|---|---|
| reels-studio:reference-analyst, trend-researcher | devices from ref1-3 (never their layouts or audio), dated desi trend notes | `refs/*.md`, `research/TRENDS_*.md` |
| viral-strategist (project) | concept + hook gates, retention map, share trigger, red-team of previews | `viral/*.md` |
| reels-studio:creative-director | brief with the look matrix and BPM grid | `BRIEF.md` |
| hinglish-scriptwriter (project) | VO story, Devanagari TTS track, Roman caption tokens, timing | `vo/*` |
| lyric-visualizer (project) | song-led reels: licensing route, beat/lyric map, line-by-line visuals | `LYRICS_*.md`, `lyrics/*` |
| reels-studio:blender-3d-artist (+ `blender-pro-reference` skill) | new props in `assets3d_jawad.py` | `<WS>/assets3d/` |
| face-compositor (project) | Jawad's 2.5D cut-outs, rim light, expression swaps | `faces25d.py`, `<module>_faces.py` |
| colorist (project) | per-reel looks on top of the kit, LUTs, finish, colour QA | `jawad_grade.py`, `luts/`, `GRADE.md` |
| reels-studio:motion-timeline-builder / motion-toolkit-engineer | reel modules / toolkit features and `jawad_kit.py` | `<module>.py` / toolkit |
| reels-studio:sound-designer, music-supervisor, caption-designer | SFX, music and VO mix, captions | `<module>_sfx.py`, `_music.py`, `captions/` |
| reels-studio:motion-qa-reviewer, delivery-packager | two-lens QA + verifier; exports | `qa/`, `reel/jawad_reels/` |

Order: references + trends -> concepts -> viral-strategist gate -> brief -> script (or lyric plan) -> viral-strategist
script gate -> TTS + timing -> parallel builds (3D, faces, grade, timelines on placeholders) -> sound -> preview
-> viral-strategist red-team + colorist check -> fixes -> master -> captions -> QA lenses -> delivery.

## Installed skills worth loading
- `motion-design` (LottieFiles, MIT): emotion -> timing/easing tables, choreography, 1/3 rules, stagger budgets.
- `video-motion-graphics` (dylantarre, MIT): Disney's 12 principles for motion graphics, AE expressions mapped
  to toolkit calls in its SOURCE.md.
- `blender-pro-reference` (RobLe3, MIT): lighting ratios, Geometry Nodes from Python, Cycles, cameras, with
  Blender 5.2 errata.
- Plugins already available: social-media-skills `hook-writer` (scoring rubric), `reels-script`,
  `viral-reverse-engineering` (share triggers), motion-reel's critique pass; reels-studio's
  `saas-motion-styles` (device recipes: use the code patterns, re-skin every look to Jawad's worlds).

## Jawad's own account skills (he added these; use them)
Synced read-only at `/root/.claude/skills/synced/52e39fd9-fc02-4eeb-bd0a-78be55c219f4_9d49974d-76ce-4345-a26f-8cb895a77bfd/<name>/`
(read `SKILL.md` first, then the `references/` it points to):
- `cinematic-director`: the director's runbook. Use it at concept and brief stage (Director's Pass that kills
  the obvious idea, short-form hook engineering, World Bible per reel, film grammar, sound-and-voice plan) and
  at screening (`references/screening-qc.md` revision protocol). Its Production Packet YAML is the format for
  each reel's packet next to `BRIEF.md`.
- `production-consistency`: one-film consistency across the five reels (asset ledger, look/identity locks,
  QC log, finishing and delivery). Its Higgsfield routing applies here ONLY to TTS (the Vlad voice); its image,
  video, upscale and Magnific paths are out of bounds for this project.
- `human-realism` + `photo-realism`: realism rules for every shot that shows Jawad (skin texture kept, no
  plastic or waxy smoothing, eye and hair detail, skin-tone-correct exposure, lens/light logic). The
  face-compositor and colorist apply them to the character-sheet cut-outs; no AI images are generated.
- `cinedance-higgsfield`: Seedance video prompting. No video is generated on Higgsfield in this project, so use
  only its film-language discipline (whole-second timelines, visible end states, blocking, gaze, lens and
  lighting locks) when writing shot lists and beat sheets.
- Reels Studio is installed as a plugin in this session (`reels-studio@jawad-reels`, local scope): its 14
  agents are `reels-studio:<agent>` and their definitions are in `plugins/reels-studio/agents/*.md`; its 4
  skills are in `plugins/reels-studio/skills/*/SKILL.md`. The toolkit copy for this page is
  `pipeline/jawad_reels/` (never edit the plugin's own toolkit).

## Brand checks before delivery (on top of the playbook checklist)
- [ ] Nothing recognisable from the fostering / Floret examples (looks, props, copy, layouts).
- [ ] Red-orange holds >= 60 % of saturated pixels (colorist hue budget); blacks deep but legal (YMIN 16-22).
- [ ] At least one serif-italic keyword moment per reel; type IVORY, never pure white.
- [ ] Hinglish reads natural to both audiences; captions match the VO tokens; no invented facts.
- [ ] Jawad's face: no halo, no warp, no uncanny motion (face-compositor limits); skin natural.
- [ ] `@jawad_mp4` end card held >= 1.5 s; cover keyword inside the 3:4 crop; AI-disclosure question answered.
