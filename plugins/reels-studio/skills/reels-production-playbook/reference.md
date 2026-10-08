# Playbook reference

The details behind SKILL.md: delegation prompts, the render queue, intake and recovery commands, QA collation,
status templates and measured numbers. In the commands, `<WS>` is the output of
`python3 -c "import core; print(core.WS)"`, run in `pipeline/<project>/`.

## 1. Delegation prompts (Agent tool, subagent_type `reels-studio:<name>`)
Each prompt needs:
- the brief path and the exact section, reel or time range;
- the files the agent owns, and that it must not touch others;
- what "done" means;
- the hand-back you expect.

Launch independent agents in the same message so they run concurrently.

**creative-director**
> Write pipeline/<project>/BRIEF.md for <client>: <n> reels of <dur> s for <platforms>; audio policy <SFX only |
> music, licence ...>. Sources: client doc <path/URL>, site <URL>, footage <folder>, reference notes <paths>. Give
> each reel a distinct look from /reels-studio:saas-motion-styles. List every ambiguous figure as an open question.

**motion-timeline-builder** (one per reel)
> Build <module>.py (reel <k>, <title>, DUR <s>, BPM <b>, LOOK <look>) from BRIEF.md §6.<k>. You own <module>.py,
> <module>_fx.py and <module>_dev.py only; the toolkit is read-only. Use labelled placeholders until
> <WS>/assets3d/<name>/<variant>/meta.json exists. Iterate at --workers 1, and don't render the full master. Hand
> back the shot list as built, the check numbers, any placeholders left, and open copy questions.

**blender-3d-artist**
> Render these assets in the shared spec: <name: variants, modes, px, notes>. Use threads 2 under nice (or the GPU
> when available) while builders share the CPU. Hand back the load calls and the sheets you checked.

**sound-designer / music-supervisor**
> <module>: events are locked (shot list in the module docstring, cues.json). Policy: <SFX only -18 LUFS | with
> music ~-14 LUFS>, <= -2.0 dBTP, 48 kHz 24-bit stem, BPM <b>. Tell me the exact render flag that keeps your
> mix (--no-sfx-build or --audio <wav>).

**motion-qa-reviewer, lens A / lens B** (two instances per reel, in parallel)
> Lens <A|B> on <WS>/out/<module>/<module>.mp4 against BRIEF.md (reel <k>). Evidence goes to
> <WS>/out/<module>/qa/<lens>/. Return the findings table and the verdict.

**motion-qa-reviewer, verify mode** (one fresh instance per blocker or major)
> verify: <finding id, time range, claim, the reporter's evidence path>. Try to refute it with your own
> measurement. Return CONFIRMED / PARTLY / NOT REPRODUCED with evidence.

**Fix round** (to the file owner)
> Confirmed findings for <module> (ids, times, evidence, suggested fix). Fix them in your files only. Prove each fix
> with a --range render over the time ±0.4 s plus the failing measurement re-run. Hand back the before and after
> numbers.

**delivery-packager**
> Package <module> as <client>_<slug> into <dest>; variants <4:5, 1:1>; cover around <t> s; SRT <yes/no>;
> branch <branch>. QA verdict: ship (report path).

## 2. Render queue (the lead only)
```bash
cd pipeline/<project>; mkdir -p <WS>/logs
free -g; uptime                                     # pick N: 4 at most on 16 GB (3 on WSL's default 8 GB)
for m in reel1 reel2 reel3; do                      # sequential: never two full renders at once
  nice -n 10 python3 render.py $m --workers 4 > <WS>/logs/$m.log 2>&1 || { echo "$m failed"; break; }
done
```
- Run the queue in the background, then poll with `tail -3 <WS>/logs/<m>.log`. The ETA is in the
  `[<module> k/n] frame ... eta` lines.
- Wait on a render with `while pgrep -f "render[.]py <module>" >/dev/null; do sleep 30; done`. The brackets stop
  the pattern from matching the pgrep command itself.
- Add `--no-sfx-build` (keep the existing SFX wav) or `--audio <mix.wav>` (use a given mix) when the sound team
  delivered a custom mix. Otherwise render.py remixes from `cues()` when the module is newer than the wav.
- After each render, check:
  - `render_stats.json`: mean and p90 s per frame, and `worker_max_rss_mb` (keep it near 2 GB or below);
  - `python3 <playbook skill folder>/qa_measure.py probe <WS>/out/<m>/<m>.mp4 --dur <DUR>` (the script sits next
    to this file).

## 3. Intake commands
```bash
D=<WS>/brand_src; mkdir -p "$D"
curl -sL "https://docs.google.com/document/d/<DOC_ID>/export?format=txt" -o "$D/client_doc.txt"   # shared doc
curl -sL -A "Mozilla/5.0" "<site URL>" -o "$D/index.html"                                         # the site
```
- Footage from a shared Drive folder: the project's setup_workspace.py has a `footage()` step that downloads the
  folder, writes `frames/<cid>/%05d.jpg` and builds a manifest. Point its folder id at the client's, through
  motion-toolkit-engineer.
- Footage from local files: put them in `<WS>/src/`. Extract with
  `ffmpeg -i <src> -vf "scale=-2:1920:flags=lanczos,format=yuvj420p" -q:v 2 -start_number 0 <WS>/frames/<cid>/%05d.jpg`,
  dropping the scale filter for sources 1920 px tall or less.
- Record the copy source of every line: a URL, or a doc and section.

## 4. QA collation format (what you give the owners)
| id | sev | reel | t (s) / frames | lens | finding | evidence (numbers + image) | verifier | owner | status |
|---|---|---|---|---|---|---|---|---|---|

Only rows where the verifier says CONFIRMED or PARTLY go to owners. NOT REPRODUCED rows stay in the table, marked
closed. After the re-render, the regression pass re-measures each row and sets its status to fixed or still open.

## 5. Status update template
```
<Project> — <stage> (<time>)
Done: <what>, see <image>.
Running: <what> — ETA <hh:mm> (<source of the estimate>).
Next: <what>, then <what>.
Need from you: <decision> (or "nothing").
```

## 6. Measured numbers (example project, cloud container, 4 cores, ~14 GB)
- Typical frame on 1 core at 1 sample: about 0.5 s. Full quality runs 1.3-4.1 s per frame per worker (3-8
  samples); previews take 0.6-0.85 s per frame. Worker peak memory was 0.9-1.8 GB on these timelines and up to
  ~2.2 GB on heavy demo scenes.
- 26 s master: 13-15 min with 4 workers, plus about 5 min of encodes. Three re-renders after QA took 15 min each, in
  sequence.
- Previews: 315 frames (21 s at 15 fps) took 195 s, and 383 frames (25.5 s) took 327 s, on 2 workers.
- 3D: about 1,000 Cycles frames (8 spp + denoise) took ~1.5 h on CPU. On a local RTX 4060 the same took 10-15 min.
- Timeline: the first complete pass of three footage reels took ~1-1.5 h in parallel; polish to the first master
  took ~0.5-1 h more. Two custom-look animations took ~3-4 h each, in parallel with their 3D props.
- QA plus fixes for three reels in parallel: ~1.3 h. The findings that mattered:
  - grey-veil flashes;
  - copy in the like/share column;
  - glow pops at hand-offs;
  - a camera snap;
  - spinning coins without spin blur;
  - particles reading as a full stop by the logo;
  - SFX true peak above -2.0 dBTP.

## 7. Recovery details
- Signs of a reset:
  - the workspace folders are missing or empty (`ls <WS>`);
  - `git log` has no local commits that you remember making;
  - background renders are gone.
- Order of restore:
  1. git (fetch and merge);
  2. `python3 setup_workspace.py` (add `--footage` if the reels use footage);
  3. the 3D archive from LFS, or re-render with the builders;
  4. SFX (render.py rebuilds from `cues()`; custom mixes come from the sound designer's build command);
  5. contact sheets to confirm.
- Prevention:
  - push after every hand-back;
  - archive 3D finals to `media/<project>/assets3d.tar` in LFS as soon as they are final;
  - keep build commands in module docstrings, so anyone can regenerate data.
- Local PC: clone into the Linux home folder, not `/mnt/c` (5-10x slower). Activate the project venv in every new
  terminal. Teleport needs a clean `git status` and a pushed branch; it carries the conversation and the branch,
  not running agents or unpushed files.

## 8. Git commands
```bash
git add <owned paths>; git commit -m "<project> <module>: <what changed>"
git fetch origin && git merge --no-edit origin/<branch>      # merge others' work; resolve keeping both intents
git push -u origin <branch>                                  # rejected? fetch + merge again. Never --force.
git lfs track "media/<project>/*.tar" "reel/<client>/*_master.mp4"; git add .gitattributes
```
On network errors, retry the push after 2, 4, 8 and 16 s.
