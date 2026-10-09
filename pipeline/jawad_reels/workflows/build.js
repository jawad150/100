export const meta = {
  name: 'jr-build',
  description: 'Build, render, two-lens QA with verify, fix loop and delivery for one @jawad_mp4 reel',
  phases: [
    { title: 'Build' }, { title: 'Preview review' }, { title: 'Fix' }, { title: 'Master' }, { title: 'QA' }, { title: 'Deliver' },
  ],
}
const A = args
const S = A.slug
const D = `/home/user/100/brand_reels/design/reels/${S}`
const W = `/home/user/100/workspace/jawad_reels/${S}`
const P = '/home/user/100/pipeline/jawad_reels'
const OUT = `/home/user/100/reel/jawad_reels/${S}`
const HEAD = `PROJECT: read /home/user/100/workspace/brand_reels/wf/ctx.txt and load the jawad-brand-reels skill (or read /home/user/100/.claude/skills/jawad-brand-reels/SKILL.md).
THIS REEL: ${A.id} "${A.title}" (slug ${S}), look ${A.look}, ${A.dur} s at 30 fps. Source of truth, in this order: ${D}/HANDOFF.md (final timings, asset paths, open items), ${D}/BRIEF.md (+ packet.yaml), ${D}/SCRIPT.md / script.json, /home/user/100/brand_reels/design/LEAD_DECISIONS.md (binding), ${D}/GATE.md, ${D}/VO_TIMING.md, ${D}/FACES.md, ${D}/SOUND.md, the series bible in /home/user/100/brand_reels/design/SLATE.md section 5. Read research docs only when the brief points to them.
FILES: this reel's code is ${P}/${S}*.py (you may create/modify only files starting with ${S}); heavy outputs in ${W}/; shared modules (jawad_kit, jawad_grade, jawad_tx, snake_captions, endcard, vo_chain, core, type3d, ui, audio, render, sprites3d, TOOLKIT.md) are READ-ONLY - work around problems locally and log them in ${D}/SHARED_REQUESTS.md. Four other reels are being built in parallel by other agents: never touch their files.
CPU: every heavy job (render.py, Blender, long whisper, big numpy renders, ffmpeg encodes of full reels) goes through ${P}/tools/heavy.sh <cmd> (global 2-slot semaphore). render.py with --workers 1. Check df -h before big outputs; delete scratch frames you no longer need.
RULES: zero mistakes - measure and LOOK at rendered frames (Read the images) before claiming anything; never anything from Organic Fostering / Floret; no invented facts; Higgsfield only for Vlad VO and only if a VO line truly must be re-taken (max 5 credits for this reel in this run, preflight with get_cost); no commits (the lead commits).`
const FSCHEMA = { type: 'object', properties: { verdict: { type: 'string', enum: ['SHIP', 'FIX'] }, findings: { type: 'array', items: { type: 'object', properties: { severity: { type: 'string', enum: ['blocker', 'major', 'minor'] }, time: { type: 'string' }, what: { type: 'string' }, evidence: { type: 'string' }, fix: { type: 'string' }, owner: { type: 'string' } }, required: ['severity', 'what', 'fix'] } } }, required: ['verdict', 'findings'] }

phase('Build')
const [build, mix] = await parallel([
  () => agent(`${HEAD}
TASK (motion-timeline-builder): build the complete reel module ${P}/${S}.py (plus any ${S}_*.py helper modules the handoff lists) to the module contract in ${P}/TOOLKIT.md (DUR, LOOK, BPM, assets(), prewarm(), pure draw(t), post(cv,t) via jawad_grade, samples(t), cues()), importing the reel's faces / sfx / music / props / captions exactly as HANDOFF.md says, with snake_captions from ${W}/vo/words.json and the end card + loop bridge. Work section by section: render stills at every beat in the beat table (render.py --stills), look at each one, fix, then a contact sheet (--sheet) of the whole reel and a low-sample preview mp4 with the rough audio mix to ${W}/preview/${S}_preview.mp4. Pass the brief's still gates first (e.g. crowd / beam-mask / exploded-stack / v1-v27 stills). Check: safe zones, type sizes, keyword per line, frame-0 rules, no empty black > 4 frames, exposure pushes not flashes, motion blur not crossing cuts, faces never uncanny, captions never over faces, end card hold >= 1.5 s, last frame loops to frame 0. Return: module paths, render cost per frame, preview path, contact sheet path, and an honest list of anything not yet at brief quality.`, { label: `build:${S}`, phase: 'Build', agentType: 'motion-timeline-builder' }),
  () => agent(`${HEAD}
TASK (music-supervisor + sound-designer duties for the final mix): resolve every BLOCKED or open AUDIO item in ${D}/HANDOFF.md (e.g. the mix crashing on a mono VO, clicks at the loop seam, duck windows still on old VO timings, loudness range and reveal contrast). Rebuild the music bed's duck windows from the measured VO in ${W}/vo/ and make a deterministic final-mix entry point ${P}/${S}_mix.py that writes, from the VO stem + SFX stem + music bed: version A (full mix) and version B (VO + SFX only, for adding a song in-app), both 48 kHz 24-bit stereo, -14 LUFS integrated (+-0.5), TP <= -2.0 dBTP, VO >= 8 LU over the bed, seamless loop seam (no click: check the sample discontinuity), plus 48 kHz stems (vo, sfx, music) into ${W}/audio/final/. Verify with ebur128 and a spectrogram you look at. Return the measured numbers and the command to regenerate.`, { label: `mix:${S}`, phase: 'Build', agentType: 'music-supervisor' }),
])

phase('Preview review')
const [viral, color] = await parallel([
  () => agent(`${HEAD}
TASK: red-team the PREVIEW of this reel before the master render: ${W}/preview/${S}_preview.mp4 and its contact sheet (paths in the builder report: ${String(build).slice(0, 2500)}). Measure frame-0 luma, VO onset, visual-change gaps, text size at phone scale, hook readability by 2.7 s, re-hooks, loop, CTA, swipe risks; look at stills you extract. Return SHIP or FIX with ranked findings (owner motion-timeline-builder unless audio).`, { label: `viral:${S}`, phase: 'Preview review', agentType: 'viral-strategist', schema: FSCHEMA }),
  () => agent(`${HEAD}
TASK: colour/finish check of the PREVIEW (${W}/preview/${S}_preview.mp4 and stills; builder report: ${String(build).slice(0, 1500)}) against the look '${A.look}' in ${P}/GRADE.md: signalstats per scene (YMIN p0.5 >= 16 on the encode, YAVG, SATAVG, HUEMED), red-orange share of saturated pixels, skin hue on Jawad's face shots, banding after a simulated CRF 23 encode, halation off type. Look at the frames. Return SHIP or FIX with findings (owner motion-timeline-builder; for a grade change the fix must be done in the reel module, not jawad_grade.py).`, { label: `color:${S}`, phase: 'Preview review', agentType: 'colorist', schema: FSCHEMA }),
])

phase('Fix')
const pre = [...((viral && viral.findings) || []), ...((color && color.findings) || [])].filter(f => f.severity !== 'minor' || /cheap|easy|trivial/i.test(f.fix || ''))
let built = build
if (pre.length) {
  built = await agent(`${HEAD}\nTASK (motion-timeline-builder): apply these pre-master findings to ${P}/${S}*.py (all blockers and majors; minors only if cheap), re-render the affected stills and the preview, look at them, and return an updated report.\nFINDINGS: ${JSON.stringify(pre).slice(0, 10000)}`, { label: `fix-pre:${S}`, phase: 'Fix', agentType: 'motion-timeline-builder' })
}

phase('Master')
const master = async (round) => agent(`${HEAD}
TASK: render the full-quality MASTER of this reel (round ${round}): render.py at the module's final sample settings through heavy.sh with --workers 1 (use --no-sfx-build only if the mix below is used), then mux with version A audio from ${P}/${S}_mix.py (regenerate it first if timings changed) into ${W}/master/${S}_master_A.mp4 (CRF 14, yuv420p, 30 fps, AAC 320k) and the same picture with version B audio into ${W}/master/${S}_master_B.mp4. Verify with ffprobe (duration = ${A.dur} s +- 1 frame, 1080x1920, 30 fps), ebur128 (-14 LUFS +-0.5, TP <= -1.5 dBTP after AAC), a 12-frame contact sheet you look at, and the first and last frames for the loop. Return paths and measurements.`, { label: `master:${S}:r${round}`, phase: 'Master', agentType: 'motion-timeline-builder' })
let m = await master(1)

phase('QA')
let qaRound = 0, shipped = false, lastQA = null
while (qaRound < 3 && !shipped) {
  qaRound++
  const lenses = await parallel([
    () => agent(`${HEAD}\nTASK: QA lens A (copy, layout, legibility, safe zones, spelling of every Roman Urdu word against SCRIPT.md, captions vs VO, end card, cover frame) on ${W}/master/${S}_master_A.mp4 (master report: ${String(m).slice(0, 1500)}). Measure; give time ranges and evidence image paths under ${W}/qa/r${qaRound}/. Return SHIP or FIX.`, { label: `qaA:${S}:r${qaRound}`, phase: 'QA', agentType: 'motion-qa-reviewer', schema: FSCHEMA }),
    () => agent(`${HEAD}\nTASK: QA lens B (motion, transitions, finish, grade, duplicate/frozen frames, motion blur across cuts, faces not uncanny, audio sync of hits to picture, VO intelligibility, loudness, loop seam picture + audio) on ${W}/master/${S}_master_A.mp4 and _B.mp4 (master report: ${String(m).slice(0, 1500)}). Measure; evidence paths under ${W}/qa/r${qaRound}/. Return SHIP or FIX.`, { label: `qaB:${S}:r${qaRound}`, phase: 'QA', agentType: 'motion-qa-reviewer', schema: FSCHEMA }),
  ])
  const all = lenses.filter(Boolean).flatMap(l => l.findings || [])
  const serious = all.filter(f => f.severity === 'blocker' || f.severity === 'major')
  // adversarial verify of each serious finding (skeptic must try to refute)
  const verified = []
  for (const f of serious.slice(0, 8)) {
    const v = await agent(`${HEAD}\nTASK: VERIFY MODE (skeptic). A QA lens reported this finding on ${W}/master/${S}_master_A.mp4: ${JSON.stringify(f)}. Re-measure it yourself from the master. Try to refute it; default to "real" only if you can reproduce it with evidence. Return JSON {"real": true|false, "evidence": "..."}.`, { label: `verify:${S}:r${qaRound}`, phase: 'QA', agentType: 'motion-qa-reviewer', schema: { type: 'object', properties: { real: { type: 'boolean' }, evidence: { type: 'string' } }, required: ['real'] } })
    if (!v || v.real) verified.push({ ...f, verify: v && v.evidence })
  }
  if (serious.length > 8) log(`${S}: ${serious.length - 8} serious findings not individually verified; passed to the fixer as reported`)
  const toFix = [...verified, ...serious.slice(8), ...all.filter(f => f.severity === 'minor')]
  lastQA = { round: qaRound, verified: verified.length, minors: all.length - serious.length }
  if (!verified.length && serious.length <= 8) { shipped = true; if (toFix.length) { await agent(`${HEAD}\nTASK (motion-timeline-builder): QA passed with only minor findings. Apply the cheap, clearly-correct minors in ${P}/${S}*.py ONLY if they do not need a re-render of more than a few seconds; otherwise leave them and list them. Findings: ${JSON.stringify(toFix).slice(0, 6000)}`, { label: `minors:${S}`, phase: 'QA', agentType: 'motion-timeline-builder' }) } break }
  await agent(`${HEAD}\nTASK (motion-timeline-builder): fix every verified QA finding below in ${P}/${S}*.py (and ${S}_mix.py for audio), re-render the affected stills, look at them, and return a report. Findings: ${JSON.stringify(toFix).slice(0, 10000)}`, { label: `qafix:${S}:r${qaRound}`, phase: 'QA', agentType: 'motion-timeline-builder' })
  m = await master(qaRound + 1)
}
log(`${S}: QA ${shipped ? 'passed' : 'did not pass'} after ${qaRound} round(s)`)

phase('Deliver')
const deliver = await agent(`${HEAD}
TASK (delivery-packager, but DO NOT git commit or push - the lead does): from ${W}/master/${S}_master_A.mp4 and _B.mp4 produce into ${OUT}/: jawad_${S}_ig.mp4 (Instagram Reels: H.264 High, 2-pass ~22 Mbps, +faststart, AAC 320k, 1080x1920, 30 fps), jawad_${S}_ig_songready.mp4 (same picture, version B audio: VO + SFX only, for adding a trending song in-app), jawad_${S}_master.mp4 (CRF 14 master), stems (vo/sfx/music wav 48 kHz 24-bit from ${W}/audio/final/), jawad_${S}_cover.jpg (the brief's cover frame, captions off if the brief says so, 1080x1920, plus a 3:4 grid-crop preview), jawad_${S}_preview.mp4 (< 30 MB, ~7 Mbps), jawad_${S}_caption.txt (the IG caption from the brief: first line, body, comment prompt, 3-5 hashtags incl. #jawadmp4, and the note "Turn on AI info: synthetic voice"), and jawad_${S}.srt from the Roman Urdu captions. Verify every file with ffprobe/ebur128. Keep the total under 300 MB (masters over 95 MB must be listed for Git LFS). Return the file list with sizes and measurements. QA status from the loop: ${JSON.stringify(lastQA)} shipped=${shipped}.`, { label: `deliver:${S}`, phase: 'Deliver', agentType: 'delivery-packager' })
return { slug: S, shipped, qa: lastQA, deliver: String(deliver).slice(0, 3000) }
