# Skills and agents: found, installed, distilled (2026-10-08)

Scope: extend the Reels Studio team (14 agents, 4 skills in `plugins/reels-studio/`) for @jawad_mp4's reels with
motion-design, SaaS animation, kinetic type, Blender, grading, Hinglish copy and retention know-how from the web
and from the locally installed plugins. Engine stays Reels Studio; nothing here is copied from the Organic
Fostering / Floret examples.

## What was added to the repo
| path | what | origin / licence |
|---|---|---|
| `.claude/agents/hinglish-scriptwriter.md` | Hinglish / Roman Urdu VO stories; Devanagari TTS track + token-aligned Roman caption track; timing on the BPM grid | new, project-specific |
| `.claude/agents/colorist.md` | per-reel looks on top of jawad_kit's `ember`/`noir_ember`, film-emulation finish in linear light, numpy .cube LUTs, signalstats / hue-budget / skin / banding checks | new |
| `.claude/agents/viral-strategist.md` | concept + hook gates, second-by-second retention map, share trigger, packaging, red-team with measurements, SHIP/FIX/KILL | new |
| `.claude/agents/face-compositor.md` | 2.5D cut-outs of the character sheets: matte + edge decontamination, layers/depth, parallax, rim light, eye-aligned swaps, never-uncanny limits | new |
| `.claude/agents/lyric-visualizer.md` | song-led reels: licensing route, beat/downbeat/section map, lyric timing, line-by-line metaphor plan, sync hierarchy | new |
| `.claude/skills/jawad-brand-reels/SKILL.md` | brand rules, the never-copy rule (itemised), paths, team map and order, brand checklist | new |
| `.claude/skills/motion-design/` | LottieFiles motion-design skill, verbatim + `LICENSE` + `SOURCE.md` (reel adaptation) | github.com/LottieFiles/motion-design-skill @ f9a8a04, MIT |
| `.claude/skills/video-motion-graphics/` | dylantarre video-motion-graphics + after-effects + filmmaker, verbatim + `LICENSE` + `SOURCE.md` (AE -> toolkit table) | github.com/dylantarre/animation-principles @ 8359713, MIT |
| `.claude/skills/blender-pro-reference/` | 5 knowledge files verbatim (lighting, geometry nodes, rendering, cameras, materials) + new SKILL.md with Blender 5.2 errata | github.com/RobLe3/cc-blender-skill @ 11016c9, MIT |

All clones live in `workspace/brand_reels/skills/src/<owner>__<repo>/` (depth 1, git-ignored, read only, never
executed). Installed copies are markdown only; a scan for `curl`, `wget`, `requests`, `urllib` and API-key
patterns in `.claude/skills/` found nothing. The new agents need no API keys and no paid services.

## Candidates reviewed
| candidate | licence | verdict | why |
|---|---|---|---|
| LottieFiles/motion-design-skill | MIT | **installed** | best-structured motion-direction skill found: personality archetypes, emotion -> easing, duration tables, choreography, 1/3 rules, quality checklist; markdown only |
| dylantarre/animation-principles (144 skills) | MIT | **3 installed** | video-motion-graphics, after-effects, filmmaker apply; the other 141 are UI/web/game variants |
| RobLe3/cc-blender-skill | MIT | **knowledge installed** | solid lighting / GN / Cycles / camera notes; its `plugin/skills` need the BlenderMCP socket (port 9876), not installed |
| browser-use/video-use | MIT | distilled only | needs an ElevenLabs API key (Scribe) for its pipeline; its hard rules and grade logic are distilled below |
| andreavolpato/agx-emulsion (spektrafilm) | GPL-3.0; LUTs custom licence | concepts only | GPL and "directly inspired by its methods" clause: no code or LUTs copied; colorist builds its own generic film curve |
| owl-listener/designer-skills | MIT | skipped | animation-principles there is a thin UI checklist, covered by LottieFiles |
| anthropics/skills | Apache-2.0 (per skill) | skipped | no video, grade or motion skill; frontend-design already available as a plugin |
| mhd347/blender-expert-skill | MIT (README) | skipped | the SKILL.md is a Blender-to-web glTF export pipeline, not rendering |
| AndreiFlau/blender-mcp-skill | GPL-3.0-or-later | skipped | drives a live Blender session through the MCP extension |
| boernmaster/blender_skill | no licence file found | skipped | remote/CUDA rendering plugin; unclear licence |
| ellmos-ai/skills `using-blender` | MIT | skipped | general German-language workflow skill; reels-studio's blender-3d-artist is more specific |
| ComposioHQ/awesome-claude-skills | index | used as an index | no relevant video, colour or Hinglish skill listed |
| Hinglish / desi copywriting skills | - | none found | web results were paid hook packs and generic hook generators; rules written from first principles + the local skills |

Search note: GitHub's search API is blocked from this session (403, session bound to configured repos), so
discovery used web search and registry pages (claudskills.com, skills.sh, claudemarketplaces.com) and repos were
cloned directly.

## Local plugin skills read (under `/root/.claude/plugins/synced/*/`)
motion-reel (SKILL.md, critique-pass prompt, voiceover reference, `lib/motion.js` springs, rig_split example),
it-reelsmaker (SKILL.md, figure.md), animation-studio (SKILL.md, storytelling, reach-and-workflow, lyric-video
starter, music cookbook), social-media-skills (hook-writer + scoring rubric, reels-script + hooks-and-retention,
viral-reverse-engineering + why-things-spread, plus caption-writer, trend-jacking, instagram-growth headers; MIT,
Frank Heijdenrijk), remotion-saas (Remotion app/SaaS templates: not about motion craft), frontend-design.
They stay installed as plugins; nothing from them was copied, only distilled.

## Distilled rules (what the new agents and the brand skill now encode)
**Motion (LottieFiles, dylantarre, motion-reel, toolkit lessons)**
- Entrances decelerate (`out_cubic`/`out_expo`), exits accelerate (`in_cubic`), on-screen moves ease both ends;
  linear only for mechanical motion. Entrances 30-50 % longer than exits.
- Anticipation 2-4 frames of counter-move; follow-through 4-8 frames on secondary layers; overshoot via springs,
  never on premium brand type. Three layers per shot: primary, secondary, ambient; counter-motion at 20-30 %.
- 1/3 rules: no move crosses more than a third of the frame without a new key; at most a third of the elements
  move at once; total stagger <= ~0.5 s (one beat at 120 BPM). 100-200 ms of stillness after a resolution.
- Something new every 2-4 s; banned template defaults: centred title on gradient, everything fading in, glow on
  UI chrome, generic particle bursts (motion-reel). Critique loop: score hook, readability at phone size (frames
  ~1/3 size: about 360 px wide for 9:16), motion, variety, brand, sync; fix the worst three; 3 rounds minimum.
- Convert UI millisecond tables to frames at 30 fps and snap to the BPM grid (SOURCE.md of the installed skills).

**SaaS product animation and kinetic type (it-reelsmaker, motion-reel, reels-studio)**
- Real UI only, never invented screens for factual claims; one display face, one UI face, one accent.
- 3-6 words on screen, a phrase is one block (15-25 px gaps, shared axis); hook <= 6 words; graphics start on
  their spoken word +-2 frames; entrance 12-16 frames, exit 8-10 frames with a 20-40 px shift.
- Jawad's house pattern: white Poppins words + one glowing Instrument Serif Italic keyword + drawn-on underline.
- Devanagari must be shaped (raqm, whole-line render); per-glyph animators can break conjuncts.

**Blender (cc-blender knowledge, verified on bpy 5.2.2)**
- Key:fill ratios 2:1 commercial, 4:1 portrait, 8:1 low-key; rim 0.5-1x key; area lights for soft light;
  emissive cards for controlled reflections (reels-studio standard) instead of HDRIs.
- Errata: Noise Texture output is `'Factor'`; `cycles.denoising_use_animation` does not exist; default view
  transform is AgX (sprite spec needs `'Standard'`); `Material.use_nodes` deprecated. CPU, OIDN, fixed seed,
  2 threads, `nice`.

**Grade and film emulation (video-use, it-reelsmaker, spektrafilm concepts, toolkit)**
- Corrective auto-grades stay within +-8 % (video-use); creative looks are explicit opt-ins. White balance
  before any LUT (it-reelsmaker). Film character comes from a log-space characteristic curve, warm toe,
  halation and grain applied after the tone curve, plus blackbody roll-off so glows get white-hot cores.
- Spatial effects (bloom, halation, grain, vignette) never go into a LUT; prove LUT orientation with an identity
  round trip; verify with signalstats, hue budget, skin hue and a simulated Instagram re-encode for banding.

**Hinglish copy (motion-reel voiceover reference + own rules)**
- Write the TTS text in the language's own script (Devanagari for a Hindi voice) and the on-screen text in the
  page's romanisation; avoid retroflex clusters in keywords for flat TTS voices; ~2.5 words/s clear, ~3 energetic.
- Hindustani middle-ground vocabulary for both audiences; no politics, religion, rivalry or colourism; facts
  about Jawad only from him.

**Retention and virality (social-media-skills, animation-studio, web)**
- Hook on three channels at once (picture, first words, on-screen text), muted-first; score Gap, Specificity,
  Truth (gate), Fit, Voice, Pull (gate); generate 5-10 across mechanisms, keep 1-2, A/B only the first 3 s.
- Retention design: no intro tax, a visual change every 2-4 s, an open loop early, a re-hook mid-reel, payoff late,
  a seamless loop and a rewatch trigger. Pacing checks (animation-studio): first movement and sound <= 1 s,
  >= 2 hits in the first 3 s, no long stretch without a change.
- Shares drive reach to non-followers: name who sends it to whom and why (identity, high-arousal emotion, social
  currency, practical value, relatability, story; Berger & Milkman, STEPPS). Copy the mechanism, never the surface;
  flag luck and account-size confounds.
- Instagram signals: watch time, likes per reach and sends per reach; Mosseri named watch time, like rate and send
  rate as top signals (reported by t3n, Feb 2025). Claims that sends now outrank everything, and the exact
  Trial Reels eligibility (1,000 followers) are secondhand blog claims: re-check in-app.

**Edit and audio correctness (video-use, it-reelsmaker)**
- 30 ms audio fades at every segment boundary; subtitles applied last; never cut inside a word; pad cut edges
  30-200 ms; mattes: 1 px erosion, 0.8 px blur, centred 3-frame alpha averaging, check frame over light and dark.
- Reels Studio's stricter mix targets win (-18 LUFS SFX-only, ~-14 LUFS with music, <= -2.0 dBTP).

**Models and licences for local work (checked 2026-10-08)**
- Depth Anything V2 Small: Apache-2.0; Base / Large / Giant: CC-BY-NC-4.0 (do not use).
- Kokoro-82M weights Apache-2.0 with Hindi voices `hf_alpha`, `hf_beta`, `hm_omega`, `hm_psi` (graded C by a
  mirror listing; voicepack data provenance unconfirmed). Indic Parler-TTS and Piper hi_IN are also being
  auditioned by the TTS owner in `workspace/brand_reels/tts/`.
- Fonts in the project: Poppins covers Devanagari; Instrument Serif and JetBrains Mono do not; none covers Urdu
  script (Nastaliq needs Noto Nastaliq Urdu). Pillow 12.3 has raqm.

## Open items for the lead
- AI disclosure: TTS voice and AI-generated character sheets likely need Meta's "AI info" label.
- CTA mechanics: "Comment JD" only if Jawad's DM automation exists.
- The TTS engine choice drives the scriptwriter's spelling (Latin vs Devanagari for English loanwords).
- The skill/agent files are not committed (per instructions); the lead commits `.claude/` and this file.

## Sources (accessed 2026-10-08)
- https://github.com/LottieFiles/motion-design-skill ; https://www.skills.sh/podo/design-agent-skills/motion-design-skill
- https://github.com/dylantarre/animation-principles ; https://www.vibeindex.ai/collection/dylantarre/animation-principles
- https://github.com/RobLe3/cc-blender-skill ; https://github.com/mhd347/blender-expert-skill ; https://github.com/AndreiFlau/blender-mcp-skill ; https://github.com/boernmaster/blender_skill ; https://github.com/ellmos-ai/skills
- https://github.com/browser-use/video-use ; https://github.com/anthropics/skills ; https://github.com/owl-listener/designer-skills ; https://github.com/ComposioHQ/awesome-claude-skills
- https://github.com/andreavolpato/agx-emulsion ; https://art.pixls.us/AgXEmulsionLutHowto
- https://snyk.io/articles/top-claude-skills-3d-modeling-game-dev-shader-programming/ ; https://claudskills.com/skills/motion-principles/
- https://huggingface.co/depth-anything/Depth-Anything-V2-Small-hf ; https://huggingface.co/depth-anything/Depth-Anything-V2-Large
- https://huggingface.co/hexgrad/Kokoro-82M ; https://replicate.com/codingayam/kokoro-82m-complete/readme
- https://t3n.de/news/reels-instagram-bewerten-mosseri-1744320/ ; https://www.socialpilot.co/blog/instagram-reels-algorithm ; https://brandid.app/blog/instagram-trial-reels/ ; https://www.tubefilter.com/2022/04/21/instagram-adam-mosseri-algorithm-change-original-content/
