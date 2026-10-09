export const meta = {
  name: 'jr-preprod',
  description: 'Pre-production for one @jawad_mp4 reel: brief, VO script, 3D props, music bed, viral gate, revisions, Vlad VO, faces, SFX cue sheet, handoff',
  phases: [
    { title: 'Brief' }, { title: 'Script+Assets' }, { title: 'Gate' }, { title: 'Revise' }, { title: 'VO' }, { title: 'Faces+SFX' }, { title: 'Handoff' },
  ],
}
const A = args
const S = A.slug
const D = `/home/user/100/brand_reels/design/reels/${S}`
const W = `/home/user/100/workspace/jawad_reels/${S}`
const P = '/home/user/100/pipeline/jawad_reels'
const RS = '/home/user/100/brand_reels/research'
const SK = '/root/.claude/skills/synced/52e39fd9-fc02-4eeb-bd0a-78be55c219f4_9d49974d-76ce-4345-a26f-8cb895a77bfd'
const REG = new Set(['viral-strategist', 'hinglish-scriptwriter', 'colorist', 'face-compositor', 'lyric-visualizer'])
function role(name, prompt, opts) {
  if (REG.has(name)) return agent(prompt, { ...opts, agentType: name })
  return agent(`You are the Reels Studio "${name}" agent. First Read /home/user/100/.claude/agents/${name}.md and follow it exactly.\n\n${prompt}`, opts)
}
const HEAD = `PROJECT: read /home/user/100/workspace/brand_reels/wf/ctx.txt first and load the jawad-brand-reels skill (or read /home/user/100/.claude/skills/jawad-brand-reels/SKILL.md).
THIS REEL: slot ${A.slot}, ${A.id} "${A.title}" (slug ${S}), look ${A.look}, BPM ${A.bpm}, DUR ${A.dur} s at 30 fps. The approved concept, fixes, faces, props and constants are in /home/user/100/brand_reels/design/SLATE.md: read section 0, section 2, section 3.${A.slot} (lines ${A.lines}), section 4 and the SERIES BIBLE (section 5) - they are binding. Panel memos for extra context: /home/user/100/brand_reels/design/panel_*.md.
FILES: design docs for this reel in ${D}/ ; per-reel code in ${P}/ named ${S}*.py (e.g. ${S}.py, ${S}_faces.py, ${S}_sfx.py, ${S}_music.py, assets3d_${S}.py); heavy outputs in ${W}/ (create it; keep this reel's workspace under 2 GB and delete intermediates). SHARED modules are READ-ONLY for you: jawad_kit.py, jawad_grade.py, jawad_tx.py, snake_captions.py, endcard.py, vo_chain.py, core.py, type3d.py, ui.py, audio.py, render.py, sprites3d.py, demo_foundation.py and TOOLKIT.md in ${P}. If you need a shared change, write it to ${D}/SHARED_REQUESTS.md and work around it locally. Four other reels are being made in parallel by other agents: never touch their files.
CPU: run every heavy job (Blender, render.py, music generation, whisper on long audio, big numpy renders) through ${P}/tools/heavy.sh <cmd> (a global 2-slot semaphore, nice 10, 2 threads); Blender scenes use threads=2. Check df -h before writing big outputs.
RESOURCES: research in ${RS}/ (cinematic_casebook_concepts.md, hooks_retention_captions.md, transitions_sound_music_bible.md, sound_design.md, face_assets.md, studio_setup.md, ref*_analysis.md, trends_india_pakistan.md, repo100_audit.md); face cut-outs + depth + metadata in /home/user/100/workspace/brand_reels/charsheet/cutouts/ with helper /home/user/100/workspace/brand_reels/charsheet/tools/faces.py; sound kit /home/user/100/workspace/brand_reels/sfx/{epic_sfx.py,epic_music.py,epic_mix.py,library/} plus ${P}/audio.py; Jawad's skills: ${SK}/cinematic-director, ${SK}/production-consistency, ${SK}/human-realism, ${SK}/photo-realism, ${SK}/cinedance-higgsfield (film-language discipline only).
RULES: zero mistakes - verify everything you produce by measuring and by looking at rendered images (Read the image files). No invented facts about Jawad. Never anything from Organic Fostering / Floret or the banned old props. No commits.`

phase('Brief')
const brief = await role('creative-director', `${HEAD}
TASK: write the PRODUCTION BRIEF for this reel: ${D}/BRIEF.md plus ${D}/packet.yaml (Jawad's cinematic-director Production Packet format: ${SK}/cinematic-director/assets/production-packet-template.yaml; World Bible per ${SK}/cinematic-director/references/world-bible.md; shot list per ${SK}/cinematic-director/assets/shot-list-template.md). It must be buildable without guessing:
- a frame-exact beat table on the BPM grid (frame numbers at 30 fps, total = DUR), hook 0-3 s spec frame by frame (frame-0 rules from SLATE section 2), re-hooks, reveal, payoff, end card (endcard.EndCard) and loop bridge to frame 0;
- every on-screen string in the house Roman Urdu spelling with style (jw_key / jw_caps / jw_body / jw_mono), px size, position (inside safe zones), in/out frames and animation (J.HouseTitle etc.);
- the VO beat plan: each VO line (Roman Urdu meaning) with target start/end time, max words (budget ~80-90 words total, hook <= 7 words landing by 2.7 s), and which on-screen moment it explains (visuals explain the VO line by line);
- transitions by catalogue id from ${RS}/transitions_sound_music_bible.md with frames, plus the jawad_tx.py function to use (read ${P}/jawad_tx.py and ${P}/TOOLKIT.md);
- the SFX cue list (sound names from epic_sfx.py / audio.py / the bible's hit stacks, align, gain) and the music plan (epic_music style, BPM, bars, sections, drop-out at the reveal, tape-stop etc.);
- 3D props spec for the blender-3d-artist (model, materials in the brand palette, lighting, camera angle(s), frames, resolution, RGBA), or "none";
- the face plan for the face-compositor (which cut-outs from SLATE, rim look A / cine look D, in/out frames, position and scale, avoid caption band);
- captions plan for snake_captions.py (chunks, keyword per chunk, hide during designed lockups, avoid rects);
- cover frame, IG caption (first line 48-55 chars restating the hook with the search keyword), 3-5 hashtags incl. #jawadmp4, comment prompt, AI-label note ("AI info" on: synthetic voice);
- a reel-specific QA acceptance checklist (measurable).
Resolve SLATE open questions with its defaults. Return a 15-line summary with the DUR, frame count and the list of agent work orders.`, { label: `brief:${S}`, phase: 'Brief' })

phase('Script+Assets')
const [script, props, music] = await parallel([
  () => role('hinglish-scriptwriter', `${HEAD}
TASK: write the VO script for this reel from ${D}/BRIEF.md (beat plan, word budget, timings). Deliver ${D}/SCRIPT.md and ${D}/script.json with: hook variants (A = SLATE hook A; B for the Trial Reel), per-beat lines {beat, start_target, end_target, roman (house spelling: bari, bohat, hai, nahi, mein), dev (Devanagari TTS text tuned for ElevenLabs v4 Hindi: nuktas where Urdu-natural, English loan words in Devanagari phonetics, numbers spelled out, commas/ellipses for pauses, JD as जे-डी if voiced), tokens (Roman caption tokens aligned 1:1 with spoken words), keyword (the serif-italic word of the line)}, total words, estimated duration at Vlad's ~2.7 words/s before the 1.06-1.10x speed-up, and a list of pronunciation-risk words to test first. Narrator is "har editor / hum / aap", never "main" about Jawad's private life. Return a short summary.`, { label: `script:${S}`, phase: 'Script+Assets' }),
  () => role('blender-3d-artist', `${HEAD}
TASK: build this reel's 3D props from the "3D props" section of ${D}/BRIEF.md (if it says none, return "none" immediately). Write a new builder module ${P}/assets3d_${S}.py (never edit other assets3d_* files; read sprites3d.py and an existing builder for the pattern) and render RGBA stills / sprite sequences into ${W}/props/ through ${P}/tools/heavy.sh with Cycles CPU, threads=2, low samples + denoise, exactly the angles/frames/resolution the brief needs. Brand palette and lighting (red-orange rim, warm practicals), premium glossy finish, physically plausible, no Organic Fostering / Floret props. Check each render over black and over FLAME orange (look at the images), report sizes and paths. Return a summary.`, { label: `props:${S}`, phase: 'Script+Assets' }),
  () => role('music-supervisor', `${HEAD}
TASK: make this reel's ORIGINAL music bed from the music plan in ${D}/BRIEF.md using /home/user/100/workspace/brand_reels/sfx/epic_music.py (read ${RS}/sound_design.md; ACE-Step in /home/user/100/workspace/brand_reels/sfx/aimusic is allowed only if the procedural bed cannot reach the brief, through heavy.sh). Exact BPM ${A.bpm}, DUR ${A.dur} s, sections on the beat table, the drop-out at the reveal, loop-friendly ending. Deliver ${W}/music/music_full.wav (48 kHz 24-bit stereo, -16 LUFS integrated, TP <= -2 dBTP) plus stems, and ${P}/${S}_music.py that regenerates it deterministically. No copyrighted or trending songs. Verify tempo/downbeats by onset analysis and loudness by ebur128; describe the spectrogram (look at it). Return a summary.`, { label: `music:${S}`, phase: 'Script+Assets' }),
])

phase('Gate')
const GSCHEMA = { type: 'object', properties: { verdict: { type: 'string', enum: ['SHIP', 'FIX', 'KILL'] }, fixes: { type: 'array', items: { type: 'object', properties: { rank: { type: 'number' }, owner: { type: 'string' }, fix: { type: 'string' }, why: { type: 'string' } }, required: ['owner', 'fix'] } }, notes: { type: 'string' } }, required: ['verdict', 'fixes'] }
const gate = await role('viral-strategist', `${HEAD}
TASK: concept + script GATE for this reel. Red-team ${D}/BRIEF.md and ${D}/SCRIPT.md / script.json against SLATE section 2 fixes, the series bible and ${RS}/hooks_retention_captions.md: three-channel hook test (visual, on-screen text, spoken line; spoken hook <= 7 words landing by 2.7 s), reason-to-stay map second by second (no visual-change gap > 2.5 s), open loop and loop bridge, share trigger, truth rule, cross-border neutrality, word budget vs DUR, keyword per line, CTA, cover, caption first line. Write ${D}/GATE.md and return the verdict with ranked fixes (owner = creative-director or hinglish-scriptwriter). KILL only if unfixable.`, { label: `gate:${S}`, phase: 'Gate', schema: GSCHEMA })

phase('Revise')
const fx = JSON.stringify((gate && gate.fixes) || []).slice(0, 8000)
await parallel([
  () => role('creative-director', `${HEAD}\nTASK: apply the viral gate's fixes owned by creative-director (and any brief change implied by script fixes) to ${D}/BRIEF.md and packet.yaml. Gate verdict ${gate && gate.verdict}; fixes: ${fx}. Keep a short CHANGELOG at the end of BRIEF.md. Return a summary.`, { label: `revise-brief:${S}`, phase: 'Revise' }),
  () => role('hinglish-scriptwriter', `${HEAD}\nTASK: apply the viral gate's fixes owned by hinglish-scriptwriter to ${D}/SCRIPT.md and script.json. Gate verdict ${gate && gate.verdict}; fixes: ${fx}. Re-check the word budget, hook length and number lock (SLATE section 4). Return a summary.`, { label: `revise-script:${S}`, phase: 'Revise' }),
])

phase('VO')
const vo = await agent(`You are the hinglish-scriptwriter for this reel (role file: /home/user/100/.claude/agents/hinglish-scriptwriter.md - read it), running with MCP access so you can call Higgsfield.\n${HEAD}
TASK: produce the FINAL VOICE-OVER for this reel with the chosen voice and measure its timing.
Voice: Higgsfield preset "Vlad" on elevenlabs_v4 - recipe, request shape and post-processing in ${P}/vo_config.json. Tools: load with ToolSearch "select:mcp__Higgsfield__generate_audio,mcp__Higgsfield__generate_audio_batch,mcp__Higgsfield__jobs_wait,mcp__Higgsfield__balance". Request params: {"model":"elevenlabs_v4","prompt":"<dev text>","dialogue":[{"text":"<dev text>","voice_id":"e5666b9c-99a2-4fac-8b4e-abee078b186d","voice_type":"preset"}]} (optional "stability"); leave use_unlim unset (answer an unlim_choice with false); omit folder_id; download result_url with curl into ${W}/vo/raw/.
HIGGSFIELD RULES: voice generation ONLY (never any image/video/other Higgsfield tool). Budget for THIS reel: at most 25 credits - preflight each request with get_cost:true (generate_audio) and keep a running sum in ${W}/vo/credits.json; GLOBAL guard: call balance first and before each batch, and if the balance is below 6800 credits, STOP generating and report (the account owner also spends credits on his own work, so never count his spend as yours: track YOUR spend from your own get_cost preflights). Never blindly resubmit; poll job ids with jobs_wait.
STEPS: (1) one batch with the pronunciation-risk words from SCRIPT.md in short carrier phrases; check with faster-whisper (language hi; decode with ffmpeg to 16 kHz mono PCM and pass the numpy array - PyAV path bug) and fix spellings; (2) generate each beat line of script.json (Devanagari) as its own take (batches of <= 12); (3) process with ${P}/vo_chain.py (read its docstring/self-test) to the vo_config post-processing spec; (4) assemble the VO stem on the beat-table timing with natural gaps (${W}/vo/vo_stem.wav, 48 kHz, -16 LUFS), (5) word timings with vo_chain's alignment onto the Roman tokens -> ${W}/vo/words.json and a per-beat timing table vs the brief targets -> ${D}/VO_TIMING.md; (6) re-take any line with CER > 0.15 or a mispronounced keyword (within budget). Report credits used, CER per line, total VO length and any beats that miss their targets by > 0.3 s.`, { label: `vo2:${S}`, phase: 'VO' })

phase('Faces+SFX')
const [faces, sfx] = await parallel([
  () => role('face-compositor', `${HEAD}
TASK: build this reel's face shots from the face plan in ${D}/BRIEF.md: ${P}/${S}_faces.py (import /home/user/100/workspace/brand_reels/charsheet/tools/faces.py by path or copy what you need into this file; follow ${RS}/face_assets.md), using only the cut-outs SLATE assigns to this reel, the reel's look '${A.look}' (from jawad_grade if registered, else jawad_kit 'ember' as stand-in and say so), rim look A / cine look D, parallax from the depth maps, light wrap, contact shadow, exposure/black matching, eye-locked hard-cut swaps, all inside never-uncanny limits; apply Jawad's human-realism and photo-realism skills (${SK}/human-realism/SKILL.md, ${SK}/photo-realism/SKILL.md): natural skin texture, no plastic smoothing. Render test stills of every face beat at its scheduled frame (through heavy.sh), look at them, fix any halo, softness or wrong scale, and write ${D}/FACES.md (API, frames, stills). Return a summary.`, { label: `faces:${S}`, phase: 'Faces+SFX' }),
  () => role('sound-designer', `${HEAD}
TASK: write this reel's SFX layer ${P}/${S}_sfx.py (toolkit audio.py conventions; cues() aligned to the brief's beat table and to the VO word timings in ${W}/vo/words.json; hero hits never on top of words; carve/duck under VO), using sounds from epic_sfx.py, audio.py and the foundation sfx library if present (${P}/sfx_jawad.py), the sound motif from SLATE, <= 3 sounds on one instant, one drop-out at the reveal. Render the SFX stem and a rough mix with ${W}/vo/vo_stem.wav and ${W}/music/music_full.wav (if present) to ${W}/audio/ (-14 LUFS, TP <= -2 dBTP; VO >= 8 LU over the bed), measure and report; write ${D}/SOUND.md (cue sheet table). Return a summary.`, { label: `sfx:${S}`, phase: 'Faces+SFX' }),
])

phase('Handoff')
const handoff = await role('creative-director', `${HEAD}
TASK: write ${D}/HANDOFF.md for the motion-timeline-builder who will build ${P}/${S}.py next: the final beat table with VO word timings from ${W}/vo/words.json and ${D}/VO_TIMING.md (shift visual beats to the measured VO where needed and say exactly which), every asset with its path (props, faces module, music, SFX module, VO stem), the captions plan, transitions with jawad_tx function names, end card params, the loop bridge, open risks, SHARED_REQUESTS if any, and the reel's QA acceptance checklist. Verify every path exists (ls). Inputs: BRIEF.md, SCRIPT.md, GATE.md, VO_TIMING.md, FACES.md, SOUND.md, the props/music reports: ${String(props).slice(0, 1500)} | ${String(music).slice(0, 1500)} | VO: ${String(vo).slice(0, 2000)} | faces: ${String(faces).slice(0, 1200)} | sfx: ${String(sfx).slice(0, 1200)}. Return a 12-line readiness summary (READY / BLOCKED items).`, { label: `handoff:${S}`, phase: 'Handoff' })
return { slug: S, brief: String(brief).slice(0, 1500), gate: gate && gate.verdict, vo: String(vo).slice(0, 1500), handoff: String(handoff).slice(0, 2500) }
