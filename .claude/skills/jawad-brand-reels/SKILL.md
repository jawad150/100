---
name: jawad-brand-reels
description: Brand rules and production map for @jawad_mp4's personal-brand Instagram Reels (Jawad, video editor and motion designer, Pakistani + Indian audience). Covers the orange + red on deep black palette and house style from his prior covers (glowing serif-italic keyword with white grotesk words, glowing underline strokes, warm dark cinematic worlds, red-orange rim light, @jawad_mp4 end card), Hinglish / Roman Urdu voice-over and captions, the five-looks rule for a set, the hard rule never to reuse the Organic Fostering or Floret examples that ship inside the toolkit, local-only production limits, and how the Reels Studio team, the five project agents and the installed skills work together on this page.
when_to_use: Load before any brief, script, design, render, grade, QA or delivery work for Jawad / @jawad_mp4 reels in this repository, and whenever a decision touches his brand colours, type, voice, captions, end card, or what may be reused from the toolkit.
---

# Jawad brand reels (@jawad_mp4)

## The page
- Jawad is a professional video editor and motion designer; the page is his own personal brand (editing,
  motion graphics, AI video, cinematic storytelling) for a Pakistani + Indian audience.
- Current job: 5 completely different reels, 30-40 s each, 1080x1920, 30 fps, Hinglish / Roman Urdu voice-over
  by a Hindi-speaking voice, cinematic visuals, SaaS-style UI motion, Blender 3D elements. Goal: 1M+ view
  potential. That is a stretch goal, never a promise in any document or caption.

## Hard rules
1. **Original, his brand only.** Never reuse the content, theme, looks, palette, props, copy or story of
   "Organic Fostering" or "Floret" (earlier clients whose work ships inside the toolkit). Concretely:
   - Never render, copy or adapt `toolkit/examples/*` (BRIEF*.md, reel1-3, anim1, anim4, demo_looks, reel_demo).
     Read them for code patterns only.
   - Never use the built-in looks as they are: `neon` (magenta/plum aurora + planet rim + dot grid), `amber`,
     `airy`, or footage grades `F.GRADES['neon'|'amber'|'airy']`. Jawad's looks are new `jw_*` keys (colorist).
     If a built-in backdrop is used as a raw layer, it is with `rim=0, dots=0` under a `jw_*` finish.
   - Never use the old prop library: heart, house, shield_check, check_tile, coin_gbp, pound_glyph, orbs,
     grad_cap, chat_bubble, key_heart, pin_phone, star_badge, logo_mark3d, question, sprout, leaf, seed,
     puzzle_pair, blocks, or the other `assets3d_*` sets' props. New props come from a new builder
     (`assets3d_jawad.py`).
   - Never use their copy or defaults: fostering, allowance, £, Ofsted, "NURTURE • DEVELOP • GROW", "A SAFE
     HOME". Always pass `header`/`title` to `ui.app_window`, text to `ui.button`, `prefix` to `T.Counter`.
   - Jawad's own earlier reel in this repo (the orange-black "Higgsfield Genjutsu" reel with blob mascots and
     "Comment JD" ending) is his, but the five new reels must not repeat its layouts or signature devices.
2. **Local only.** No Higgsfield tools, no paid generation (Magnific, Kling, Creative-Claw, ElevenLabs or any
   other credit-spending connector). Blender (bpy 5.2, CPU), Python 3.13, ffmpeg, Node 22, faster-whisper, local
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

**House type** (as on his covers):
- Keyword: Instrument Serif Italic, glowing flame, one per line, ~1.3-1.8x the grotesk cap height. In the
  toolkit it is `font='hand'` (project.json maps Caveat -> InstrumentSerif-Bold, a copy of RegularItalic):
  `T.render('yaadein', 'deep_glow', px=150, font='hand', fill=('GOLD', 'FLAME'), glow_color=('FLAME', 2.0))`.
- Grotesk: Poppins SemiBold/Bold uppercase, IVORY, slight tracking (`font='ui'` / `'ui_bold'`; `'display'` =
  Poppins Black). Mono for UI and timecodes: JetBrains Mono.
- Pattern: `KUCH {yaadein}` / `delete {nahi} hoti`: white grotesk words + the serif keyword on a shared baseline,
  then a glowing flame underline stroke drawn on (`ui.stroke_mask` + `ui.trim_polyline`, tapered, `K.glow`).
- Signature: `@jawad_mp4` in Poppins Medium, IVORY ~80 %, under the final line on the end card and on covers.
- Sizes and zones from the playbook: hero >= 130 px, keyword lines measured with `T.measure(..., font='hand')`,
  <= 940 px wide (780 px in y 1050-1700), key copy in x 70-1010, y 230-1480.

**World and light:** warm dark cinematic spaces (studio, edit suite, void with volumetric flame light, god rays,
haze), bokeh and dust (`K.Particles` in FLAME/GOLD, kept off type), red-orange rim light on Jawad and on props,
dark-glass SaaS UI with flame edges and comet sweeps (timelines, keyframes, render bars, export dialogs, cursors),
Blender props in black gloss + emissive orange or chrome reflecting flame, film grain and halation from the
`jw_*` finish. No full-frame white flashes; exposure pushes on cut frames.

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
Each reel gets its own story shape, look (`jw_ember`, `jw_inferno`, `jw_gold_hour`, `jw_noir_flame`, `jw_dusk`
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
| colorist (project) | `jw_*` looks, LUTs, finish, colour QA | `jawad_grade.py`, `luts/`, `GRADE.md` |
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
  `saas-motion-styles` (device recipes: use the code patterns, re-skin every look to the `jw_*` worlds).

## Brand checks before delivery (on top of the playbook checklist)
- [ ] Nothing recognisable from the fostering / Floret examples (looks, props, copy, layouts).
- [ ] Red-orange holds >= 60 % of saturated pixels (colorist hue budget); blacks deep but legal (YMIN 16-22).
- [ ] At least one serif-italic keyword moment per reel; type IVORY, never pure white.
- [ ] Hinglish reads natural to both audiences; captions match the VO tokens; no invented facts.
- [ ] Jawad's face: no halo, no warp, no uncanny motion (face-compositor limits); skin natural.
- [ ] `@jawad_mp4` end card held >= 1.5 s; cover keyword inside the 3:4 crop; AI-disclosure question answered.
