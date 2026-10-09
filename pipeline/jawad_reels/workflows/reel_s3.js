export const meta = {
  name: 'jr-reel-s3',
  description: 'Session 3: finish pre-production where needed (faces, audio on the rebuilt kit, handoff), then build, preview review, master, two-lens QA with adversarial verify, and deliver one @jawad_mp4 reel to reel/jawad_reels/<slug>/ (committed and pushed)',
  phases: [
    { title: 'Pre-production' }, { title: 'Handoff' }, { title: 'Build' }, { title: 'Preview review' }, { title: 'Fix' }, { title: 'Master' }, { title: 'QA' }, { title: 'Deliver' },
  ],
}
const A = args
const S = A.slug
const D = `/home/user/100/brand_reels/design/reels/${S}`
const W = `/home/user/100/workspace/jawad_reels/${S}`
const P = '/home/user/100/pipeline/jawad_reels'
const WF = '/home/user/100/workspace/brand_reels/wf'
const OUT = `/home/user/100/reel/jawad_reels/${S}`
const KIT = `${WF}/KIT_READY`
const COMMIT = `${P}/tools/commit_step.sh`
const SK = '/root/.claude/skills/synced/52e39fd9-fc02-4eeb-bd0a-78be55c219f4_9d49974d-76ce-4345-a26f-8cb895a77bfd'
const NF = Math.round(A.dur * 30)
function role(name, prompt, opts) {
  return agent(`You are the "${name}" agent of the Reels Studio team: first Read /home/user/100/.claude/agents/${name}.md and follow it (where it conflicts with this task, this task wins).\n\n${prompt}`, opts)
}
const HEAD = `PROJECT: read ${WF}/ctx.txt first and load the jawad-brand-reels skill (or read /home/user/100/.claude/skills/jawad-brand-reels/SKILL.md).
THIS REEL: ${A.id} "${A.title}" (slug ${S}), look ${A.look}, ${A.dur} s at 30 fps (${NF} frames). Source of truth, in this order: ${D}/HANDOFF.md (final timings, asset paths, open items), ${D}/BRIEF.md (+ packet.yaml), ${D}/SCRIPT.md / script.json, /home/user/100/brand_reels/design/LEAD_DECISIONS.md (BINDING), ${D}/GATE.md, ${D}/VO_TIMING.md, ${D}/FACES.md, ${D}/SOUND.md, and /home/user/100/brand_reels/design/SLATE.md (section 3.${A.slot} for this reel, section 5 = SERIES BIBLE). Read research docs only when the brief points to them.
FILES: this reel's code is ${P}/${S}*.py (you may create / modify only files whose name starts with ${S}); design docs in ${D}/; heavy outputs in ${W}/ (keep it under ~4 GB; delete scratch frames you no longer need). Shared modules (jawad_kit, jawad_grade, jawad_tx, snake_captions, endcard, vo_chain, core, type3d, ui, audio, render, sprites3d, sfx_jawad, epic_sfx, epic_music, epic_mix, TOOLKIT.md) are READ-ONLY: work around problems locally and log them in ${D}/SHARED_REQUESTS.md. Four other reels are being built in parallel by other agents: never touch their files.
SOUND KIT: epic_sfx / epic_music / epic_mix were lost and are being rebuilt in ${P} by another workflow; use them only once ${KIT} exists. To wait, call \`python3 ${P}/tools/wait_for.py ${KIT} 580\` in the FOREGROUND (Bash timeout 600000) and repeat until it exits 0 (up to 8 hours); do your non-audio work first. Then read it (status + open defects) and ${WF}/kit_reel_issues.json for items on this reel. LUFS / gain numbers in the design docs were measured on the OLD kit: re-measure, never trust them. Kit problems you hit: write them to ${WF}/kit_bugs/${S}.md and work around them in ${S}_*.py.
CPU: every heavy job (render.py, Blender, long whisper, big numpy renders, full-reel ffmpeg encodes) goes through ${P}/tools/heavy.sh <cmd> (global 2-slot semaphore across all agents, nice 10, 2 threads); render.py with --workers 1. Check df -h before big outputs.
HIGGSFIELD: only for a Vlad VO re-take of a mispronounced or unclear word (LEAD_DECISIONS 3), at most 5 credits for this reel in this session. Tools via ToolSearch "select:mcp__Higgsfield__generate_audio,mcp__Higgsfield__jobs_wait,mcp__Higgsfield__balance"; recipe and request shape in ${P}/vo_config.json; preflight every request with get_cost:true; log each spend in ${W}/vo/credits_s3.json (shared by every agent of this reel: read its running total first and never let it pass 5); never resubmit blindly; never any other Higgsfield tool.
GIT: when your step's files are final, commit + push them with ${COMMIT} "${S}: <one-line message>" <paths...> - only your own files (${P}/${S}*.py, ${D}/..., and at delivery ${OUT}/); never workspace/, never other reels' files; never run git add / commit / push directly.
RULES: zero mistakes - measure, and LOOK at rendered frames (Read the images) before claiming anything; never anything from Organic Fostering / Floret; no invented facts about Jawad; LEAD_DECISIONS 7: speed over gold-plating (list a minor finding instead of a long re-render when a viewer would not see it at phone size).`
const FSCHEMA = { type: 'object', properties: { verdict: { type: 'string', enum: ['SHIP', 'FIX'] }, findings: { type: 'array', items: { type: 'object', properties: { severity: { type: 'string', enum: ['blocker', 'major', 'minor'] }, time: { type: 'string' }, what: { type: 'string' }, evidence: { type: 'string' }, fix: { type: 'string' }, owner: { type: 'string' } }, required: ['severity', 'what', 'fix'] } } }, required: ['verdict', 'findings'] }

let pre = null, handoff = null
if (A.handoff) {
  phase('Pre-production')
  const jobs = []
  if (A.faces) jobs.push(() => role('face-compositor', `${HEAD}
TASK (pre-production): build this reel's face shots from the face plan in ${D}/BRIEF.md (section "Face plan"): write ${P}/${S}_faces.py (import /home/user/100/workspace/brand_reels/charsheet/tools/faces.py BY PATH under a private module name, the way ${P}/log_kya_kahenge_faces.py and ${P}/bijli_chali_gayi_faces.py do; follow /home/user/100/brand_reels/research/face_assets.md), using only the cut-out the brief assigns, the reel's look '${A.look}' (jawad_grade), rim look A / cine look D, parallax from the depth map, light wrap, contact shadow, exposure / black matching, all inside never-uncanny limits; apply ${SK}/human-realism/SKILL.md and ${SK}/photo-realism/SKILL.md (natural skin texture, no plastic smoothing). Note: workspace/brand_reels/charsheet/crops/ is reconstructed from the cut-outs (see ${P}/tools/rebuild_crops.py). Provide exactly the API the brief names (e.g. face_layers() and its outputs). Render test stills of every face beat at its scheduled frame (through heavy.sh), look at them at 100 % and at phone size, fix any halo, softness or wrong scale, write ${D}/FACES.md (API, frames, stills, measurements), and commit ${P}/${S}_faces.py ${D}/FACES.md. Return a summary.`, { label: `faces:${S}`, phase: 'Pre-production', effort: 'high' }))
  jobs.push(() => role('sound-designer', `${HEAD}
TASK (pre-production audio on the rebuilt kit; you also play music-supervisor, /home/user/100/.claude/agents/music-supervisor.md): wait for the kit (SOUND KIT above). Then regenerate this reel's music bed with ${P}/${S}_music.py (its documented render / verify entry points) into ${W}/music/ (music_full.wav + stems + verify json), and the SFX stem + rough mixes A (VO + SFX + music) and B (VO + SFX) with ${P}/${S}_sfx.py (its render / rough entry points) into ${W}/audio/, using the restored VO in ${W}/vo/. Measure against LEAD_DECISIONS item 1 and the reel's own targets in ${D}/SOUND.md and ${D}/MUSIC*.md (BPM grid, drop-out at the reveal, loop seam, -16 LUFS bed, -14 LUFS mixes, TP, VO over bed on every word); look at the spectrograms. Fix only ${S}_*.py (e.g. re-tune cue gains or the bed level for the new kit). Append a section "Session 3: audio on the rebuilt kit" to ${D}/SOUND.md with the new numbers and exact paths, then commit ${P}/${S}_music.py ${P}/${S}_sfx.py ${D}/SOUND.md. Return paths + numbers + anything still open.`, { label: `audio:${S}`, phase: 'Pre-production', effort: 'high' }))
  pre = await parallel(jobs)
  phase('Handoff')
  handoff = await role('creative-director', `${HEAD}
TASK (pre-production handoff): write ${D}/HANDOFF.md for the motion-timeline-builder who builds ${P}/${S}.py next. Use ${D}/../log_kya_kahenge/HANDOFF.md and ${D}/../pehle_wala/HANDOFF.md as the format. Contents: the final beat table with the VO word timings from ${W}/vo/words.json (and the other *.words.json there) and ${D}/VO_TIMING.md (shift picture beats to the measured VO where needed and say exactly which - LEAD_DECISIONS 3: picture moves to the VO); every asset with its path (props / assets3d renders in ${W}/, the faces module, music bed, SFX module, VO stem); the captions plan (snake_captions); transitions with jawad_tx function names; end card params; the loop bridge; open risks; SHARED_REQUESTS if any; and the reel's measurable QA acceptance checklist. Verify that every path exists (ls) and that each module imports. Inputs: BRIEF.md, packet.yaml, SCRIPT.md, script.json, GATE.md, VO_TIMING.md, FACES.md, SOUND.md, MUSIC*.md and these stage reports: ${JSON.stringify((pre || []).map(x => String(x).slice(0, 2500)))}. Commit ${D}/HANDOFF.md. Return a 12-line readiness summary (READY / BLOCKED items).`, { label: `handoff:${S}`, phase: 'Handoff', effort: 'high' })
}

phase('Build')
const [build, mix] = await parallel([
  () => role('motion-timeline-builder', `${HEAD}
TASK: build the complete reel module ${P}/${S}.py (plus any ${S}_*.py helper modules the handoff lists) to the module contract in ${P}/TOOLKIT.md (DUR, LOOK, BPM, assets(), prewarm(), pure draw(t), post(cv, t) via jawad_grade, samples(t), cues()), importing the reel's faces / sfx / music / props / captions exactly as ${D}/HANDOFF.md says, with snake_captions from ${W}/vo/words.json and the end card + loop bridge.${A.handoff ? '' : ` If ${P}/${S}.py already exists it is the previous session's in-progress build: read it and its helpers fully, keep what works, and finish it.`} Work section by section: render stills at every beat in the beat table (render.py --stills), look at each one, fix, then a contact sheet (--sheet) of the whole reel and a low-sample preview mp4 to ${W}/preview/${S}_preview.mp4 muxed with the newest rough mix in ${W}/audio/ (or the VO stem alone if no mix exists yet). Pass the brief's still gates first. Check: safe zones, type sizes, keyword per line, frame-0 rules, no empty black > 4 frames, exposure pushes not flashes, motion blur not crossing cuts, faces never uncanny, captions never over faces, end card hold >= 1.5 s, last frame loops to frame 0. Commit ${P}/${S}*.py (your files only) once the preview exists. Return: module paths, render cost per frame, preview path, contact sheet path, and an honest list of anything not yet at brief quality.`, { label: `build:${S}`, phase: 'Build', effort: 'max' }),
  () => role('music-supervisor', `${HEAD}
TASK (final mix; you also play sound-designer, /home/user/100/.claude/agents/sound-designer.md): wait for the kit (SOUND KIT above).${A.handoff ? ` The pre-production audio stage already regenerated the bed and the SFX stem on the rebuilt kit (see ${D}/SOUND.md "Session 3").` : ` First regenerate this reel's music bed (${P}/${S}_music.py) into ${W}/music/ and the SFX stem (${P}/${S}_sfx.py) into ${W}/audio/ on the rebuilt kit, measure them, and append "Session 3: audio on the rebuilt kit" (numbers + paths) to ${D}/SOUND.md.`} Resolve every BLOCKED or open AUDIO item in ${D}/HANDOFF.md (e.g. a mono VO, clicks at the loop seam, duck windows on old VO timings, loudness range, reveal contrast). Rebuild the bed's duck windows from the measured VO in ${W}/vo/ and make (or finish) a deterministic final-mix entry point ${P}/${S}_mix.py that writes, from the VO stem + SFX stem + music bed: version A (full mix) and version B (VO + SFX only, for adding a song in-app), both 48 kHz 24-bit stereo, -14 LUFS integrated (+-0.5), TP <= -2.0 dBTP, VO >= 8 LU over the bed (LEAD_DECISIONS 1), seamless loop seam (check the sample discontinuity), plus 48 kHz stems (vo, sfx, music) into ${W}/audio/final/. Verify with ebur128 and a spectrogram you look at. Commit ${P}/${S}_mix.py (and any ${S}_*.py audio file you changed) + ${D}/SOUND.md. Return the measured numbers and the command to regenerate.`, { label: `mix:${S}`, phase: 'Build', effort: 'high' }),
])

phase('Preview review')
const [viral, color] = await parallel([
  () => role('viral-strategist', `${HEAD}
TASK (do not edit code): red-team the PREVIEW of this reel before the master render: ${W}/preview/${S}_preview.mp4 and its contact sheet (paths in the builder report: ${String(build).slice(0, 2500)}). Measure frame-0 luma, VO onset, visual-change gaps, text size at phone scale, hook readability by 2.7 s, re-hooks, loop, CTA, swipe risks; look at stills you extract. Return SHIP or FIX with ranked findings (owner motion-timeline-builder unless audio).`, { label: `viral:${S}`, phase: 'Preview review', schema: FSCHEMA, effort: 'high' }),
  () => role('colorist', `${HEAD}
TASK (do not edit code): colour / finish check of the PREVIEW (${W}/preview/${S}_preview.mp4 and stills; builder report: ${String(build).slice(0, 1500)}) against the look '${A.look}' in ${P}/GRADE.md: signalstats per scene (Y p0.5 >= 16 on the encode per LEAD_DECISIONS 2, YAVG, SATAVG, HUEMED), red-orange share of saturated pixels, skin hue on Jawad's face shots, banding after a simulated CRF 23 encode, halation off type. Look at the frames. Return SHIP or FIX with findings (owner motion-timeline-builder; a grade change must be made in the reel module, not jawad_grade.py).`, { label: `color:${S}`, phase: 'Preview review', schema: FSCHEMA, effort: 'high' }),
])

phase('Fix')
const preFind = [...((viral && viral.findings) || []), ...((color && color.findings) || [])].filter(f => f.severity !== 'minor' || /cheap|easy|trivial/i.test(f.fix || ''))
let built = build
if (preFind.length) {
  built = await role('motion-timeline-builder', `${HEAD}
TASK: apply these pre-master findings to ${P}/${S}*.py (all blockers and majors; minors only if cheap), re-render the affected stills and the preview, look at them, commit your files, and return an updated report.
FINDINGS: ${JSON.stringify(preFind).slice(0, 10000)}`, { label: `fix-pre:${S}`, phase: 'Fix', effort: 'max' })
}

phase('Master')
const master = (round) => role('motion-timeline-builder', `${HEAD}
TASK: render the full-quality MASTER of this reel (round ${round}): render.py at the module's final sample settings through heavy.sh with --workers 1 (use --no-sfx-build since the final mix below is used), then mux with version A audio from ${P}/${S}_mix.py (regenerate it first if timings changed) into ${W}/master/${S}_master_A.mp4 (CRF 14, yuv420p, 30 fps, AAC 320k) and the same picture with version B audio into ${W}/master/${S}_master_B.mp4. If a previous round's master exists and the fixes since then are local, you may re-render only the affected time ranges and splice them losslessly into the previous intermediate (prove the splice is frame-exact). Verify with ffprobe (duration = ${A.dur} s +- 1 frame, 1080x1920, 30 fps), ebur128 (-14 LUFS +-0.5, TP <= -1.5 dBTP after AAC), a 12-frame contact sheet you look at, and the first and last frames for the loop. Commit any ${S}*.py you changed. Return paths and measurements.`, { label: `master:${S}:r${round}`, phase: 'Master', effort: 'high' })
let m = await master(1)

phase('QA')
const VSCH = { type: 'object', properties: { real: { type: 'boolean' }, evidence: { type: 'string' } }, required: ['real', 'evidence'] }
let qaRound = 0, shipped = false, lastQA = null, openFindings = []
while (qaRound < 3 && !shipped) {
  qaRound++
  const lenses = await parallel([
    () => role('motion-qa-reviewer', `${HEAD}\nTASK (do not edit code): QA lens A - copy, layout, legibility, safe zones, spelling of every Roman Urdu word against SCRIPT.md, captions vs VO, end card, cover frame - on ${W}/master/${S}_master_A.mp4 (master report: ${String(m).slice(0, 1500)}). Measure; give time ranges and evidence image paths under ${W}/qa/r${qaRound}/. Return SHIP or FIX.`, { label: `qaA:${S}:r${qaRound}`, phase: 'QA', schema: FSCHEMA, effort: 'high' }),
    () => role('motion-qa-reviewer', `${HEAD}\nTASK (do not edit code): QA lens B - motion, transitions, finish, grade, duplicate / frozen frames, motion blur across cuts, faces not uncanny, audio sync of hits to picture, VO intelligibility, loudness, loop seam picture + audio - on ${W}/master/${S}_master_A.mp4 and _B.mp4 (master report: ${String(m).slice(0, 1500)}). Measure; evidence paths under ${W}/qa/r${qaRound}/. Return SHIP or FIX.`, { label: `qaB:${S}:r${qaRound}`, phase: 'QA', schema: FSCHEMA, effort: 'high' }),
  ])
  const all = lenses.filter(Boolean).flatMap(l => l.findings || [])
  const serious = all.filter(f => f.severity === 'blocker' || f.severity === 'major')
  const checks = await parallel(serious.slice(0, 10).map((f, i) => () => role('motion-qa-reviewer', `${HEAD}\nTASK (VERIFY MODE, skeptic; do not edit code): a QA lens reported this finding on ${W}/master/${S}_master_A.mp4: ${JSON.stringify(f)}. Re-measure it yourself from the master. Try to refute it; answer real=true only if you can reproduce it with evidence (and it matters at phone size per LEAD_DECISIONS 7).`, { label: `verify:${S}:r${qaRound}:${i}`, phase: 'QA', schema: VSCH, effort: 'high' })))
  const verified = serious.slice(0, 10).map((f, i) => ({ ...f, verify: checks[i] })).filter(x => !x.verify || x.verify.real)
  if (serious.length > 10) log(`${S}: ${serious.length - 10} serious findings not individually verified; passed to the fixer as reported`)
  const toFix = [...verified, ...serious.slice(10)]
  const minors = all.filter(f => f.severity === 'minor')
  lastQA = { round: qaRound, serious: serious.length, verified: toFix.length, minors: minors.length }
  if (!toFix.length) {
    shipped = true
    if (minors.length) await role('motion-timeline-builder', `${HEAD}\nTASK: QA passed with only minor findings. Apply the cheap, clearly-correct minors in ${P}/${S}*.py ONLY if they need no re-render of more than a few seconds (then re-render just that range, splice it into ${W}/master/${S}_master_A.mp4 and _B.mp4 frame-exactly and re-verify duration / loudness); otherwise leave them and list them. Commit your files. Findings: ${JSON.stringify(minors).slice(0, 6000)}`, { label: `minors:${S}`, phase: 'QA', effort: 'high' })
    break
  }
  openFindings = toFix
  await role('motion-timeline-builder', `${HEAD}\nTASK: fix every verified QA finding below in ${P}/${S}*.py (and ${S}_mix.py for audio), re-render the affected stills, look at them, commit your files, and return a report. Findings: ${JSON.stringify(toFix).slice(0, 10000)}`, { label: `qafix:${S}:r${qaRound}`, phase: 'QA', effort: 'max' })
  m = await master(qaRound + 1)
}
log(`${S}: QA ${shipped ? 'passed' : 'did NOT pass'} after ${qaRound} round(s)`)

phase('Deliver')
let deliver = null
if (shipped) {
  deliver = await role('delivery-packager', `${HEAD}
TASK: from ${W}/master/${S}_master_A.mp4 and _B.mp4 produce into ${OUT}/: jawad_${S}_ig.mp4 (Instagram Reels: H.264 High, 2-pass at the highest bitrate that keeps the file <= 90 MB (about 18-20 Mbps video), +faststart, AAC 320k 48 kHz, 1080x1920, 30 fps), jawad_${S}_ig_songready.mp4 (same picture, version B audio: VO + SFX only, for adding a trending song in-app; same size rule), jawad_${S}_master.mp4 (CRF 14 master; if it is >= 94 MB re-encode it at CRF 14 with -maxrate 20M -bufsize 40M so it stays under 94 MB, and say so), stems/ (vo, sfx, music wav 48 kHz 24-bit from ${W}/audio/final/), jawad_${S}_cover.jpg (the brief's cover frame, captions off if the brief says so, 1080x1920) plus jawad_${S}_cover_grid_3x4.jpg (the 3:4 grid crop), jawad_${S}_caption.txt (the IG caption from the brief: first line, body, comment prompt, 3-5 hashtags incl. #jawadmp4, and the note "Turn on AI info: synthetic voice"), and jawad_${S}.srt from the Roman Urdu captions (word timings in ${W}/vo/). NO preview mp4 (Jawad asked for no previews). Every file must be < 95 MB (GitHub's limit; no LFS). Verify every file with ffprobe / ebur128 (IG files: -14 LUFS +-0.5, TP <= -1.5 dBTP; duration ${A.dur} s +- 1 frame). Write ${OUT}/README.md (one table: file, size, what it is, measurements; QA: passed in round ${qaRound}). Then UPLOAD: ${COMMIT} "${S}: deliver final reel (QA passed)" ${OUT} - this is the hand-off to Jawad, so confirm the push succeeded (the script prints the commit line). Return the file list with sizes, measurements and the commit line.`, { label: `deliver:${S}`, phase: 'Deliver', effort: 'high' })
} else {
  log(`${S}: not delivered - open findings returned to the lead`)
}
return { slug: S, shipped, qa: lastQA, open: shipped ? [] : openFindings, deliver: String(deliver).slice(0, 3000), handoff: String(handoff).slice(0, 1500), build: String(built).slice(0, 2000), mix: String(mix).slice(0, 1500) }