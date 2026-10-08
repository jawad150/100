---
description: Scaffolds a new client motion-reel project in the current repository from the reels-studio toolkit. It copies the Python motion toolkit (3D compositor, type, SaaS UI kit, footage, Blender prop builders, SFX library, renderer, packager) into pipeline/<project>/, writes project.json (workspace folder, brand palette roles, font map, site, Drive footage folder, delivery folder), sets up .gitignore and Git LFS for masters, checks the Python, Blender and ffmpeg dependencies, builds the brand kit and workspace, runs the self-tests, and hands over to the creative director for the brief.
when_to_use: Use when the user starts videos for a new client or brand, says "new project", "set up the toolkit here", "start reels for <client>", or when a repository has no pipeline/<project>/ toolkit folder yet. Also use it to refresh an existing project's toolkit from a newer plugin version.
argument-hint: <project-slug> [client website URL] [Drive footage folder URL]
---

# New reel project

The toolkit lives in `${CLAUDE_PLUGIN_ROOT}/toolkit/`. Each project gets its own copy in `pipeline/<project>/`, so a
project keeps working even after the plugin is updated, and project-specific fixes stay in that project.
Helper scripts: `${CLAUDE_SKILL_DIR}/brandkit.py` (brand scan, fonts, logos, contrast, brand sheet).

## 1. Collect (ask once, as one list; skip what the user already said)
- Project slug: lowercase, underscores (`acme_launch`). The client's display name.
- Website URL, brand guide, logo files, content doc (Google Doc: export with `.../export?format=txt`).
- Footage: a Google Drive folder shared as "anyone with the link", local files, or none (pure animation).
- Deliverables: count, length (usually 20–30 s), 9:16 1080x1920 30 fps, other aspect ratios, deadline.
- Audio policy: SFX only, SFX + music, or voice-over. Captions: yes or no.
- Reference reels the client likes.

## 2. Copy the toolkit
```bash
P=<project-slug>; T="${CLAUDE_PLUGIN_ROOT}/toolkit"
[ -d "$T" ] || T=$(dirname "$(find ~/.claude/plugins -name wsconf.py -path '*reels-studio*toolkit*' | head -1)")
mkdir -p pipeline/$P && cp -n "$T"/*.py "$T"/*.md "$T"/*.sh pipeline/$P/ 2>/dev/null; cp -rn "$T"/examples pipeline/$P/
ls pipeline/$P
```
`cp -n` never overwrites. `examples/` holds finished timelines from earlier projects (reels and animations): read
them for patterns, never render them in a new project, because their copy and brand belong to another client.

## 3. project.json (committed)
Write `pipeline/$P/project.json`:
```json
{
  "project": "<slug>",
  "workspace": "workspace_<slug>",
  "site": "https://client.com",
  "drive_folder": "<Drive folder id or omit>",
  "google_fonts": {"Inter": "Inter:wght@400;500;600;700;800;900", "Kalam": "Kalam:wght@700"},
  "font_map": {"Nunito": "Inter", "Poppins": "Inter", "Caveat": "Kalam"},
  "logo_src": "https://client.com/logo.svg",
  "palette": {},
  "deliver": {"dir": "reel/<slug>", "prefix": "<slug>"}
}
```
- `workspace` is the git-ignored data folder (fonts, logos, footage frames, 3D renders, audio, renders), relative to
  the repo root. `FOSTER_WS=/path` overrides it for one shell.
- `palette` and `font_map` are filled in by the brand-kit-builder agent (step 5). The palette keys are colour roles
  (MAGENTA = primary, ORANGE = accent, LEAF = secondary, INK = dark text, IVORY = light, NIGHT_0/1 = darkest…); see
  that agent for the full table. The `google_fonts` keys are the file prefixes that `font_map` points to.
- Keys you omit fall back to the toolkit defaults, which are the Organic Fostering brand. Fill every one.

## 4. Repository setup
```bash
grep -qx "workspace_$P/" .gitignore 2>/dev/null || echo "workspace_$P/" >> .gitignore
grep -q "reel/$P/\*_master.mp4" .gitattributes 2>/dev/null || \
  echo "reel/$P/*_master.mp4 filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
printf '__pycache__/\n*.pyc\n' >> .gitignore; sort -u -o .gitignore .gitignore
git lfs install --local 2>/dev/null || echo "install git-lfs (apt install git-lfs / brew install git-lfs)"
```

## 5. Dependencies
Check, then install only what is missing (ask before installing system packages):
```bash
python3 -c "import numpy, cv2, PIL, scipy, cairosvg, fontTools; print('python deps ok')"
python3 -c "import bpy; print('bpy', bpy.app.version_string)"   # Blender as a module, for 3D props
ffmpeg -version | head -1; ffprobe -version | head -1
```
- Python packages, in a venv: `uv venv --python 3.13 .venv && . .venv/bin/activate && uv pip install bpy==5.2.2
  numpy opencv-python-headless pillow scipy cairosvg fonttools imageio-ffmpeg`. bpy 5.2 needs Python 3.13.
- System: ffmpeg, git-lfs, and libcairo2 for cairosvg (`sudo apt install ffmpeg git-lfs libcairo2` on Ubuntu/WSL,
  `brew install ffmpeg git-lfs cairo` on macOS).
- An NVIDIA GPU makes 3D props about 10× faster: check `nvidia-smi`, then set `FOSTER_GPU=1` for the Blender builders.

## 6. Brand kit and workspace
1. Run the **reels-studio:brand-kit-builder** agent with the slug, site, logo files and content doc. It fills
   `palette` and `font_map`, downloads the fonts and logos into the workspace, and writes `pipeline/$P/BRAND.md`.
2. Then, in `pipeline/$P/`: `python3 setup_workspace.py` (fonts, logo, site photos from project.json) and, with footage,
   `python3 setup_workspace.py --footage` (Drive folder → `frames/cXX/%05d.jpg` + `manifest.json`). Re-run it after a
   fresh clone or a reset container; the workspace is never committed.
3. Verify: `python3 -c "import core; print(core.WS, core.PALETTE_HEX['MAGENTA'], core.font_path('Nunito-Black'))"`
   prints the new workspace, the brand primary and a font file that exists.

## 7. Self-tests
In `pipeline/$P/`, run `python3 <module>.py selftest` for core, type3d, ui, sprites3d (needs at least one 3D asset),
footage (needs frames) and audio. Open the PNGs in `<WS>/out/selftest/`: the type, glass UI and looks must show the
new brand colours and fonts. Then `python3 render.py reel_demo --sheet 12` for an end-to-end render check.

## 8. Hand over
- Commit `pipeline/$P/` (code, project.json, BRAND.md), `.gitignore` and `.gitattributes`, then push.
- Next: reference-analyst (if the client shared references) and trend-researcher, then **creative-director** writes
  `pipeline/$P/BRIEF.md`. The reels-production-playbook skill has the full order of work.
- 3D props: blender-3d-artist renders from the builders (`assets3d_icons.py all`, etc.), which read `brand/` and the
  palette. Archive finished renders with `tar -cf media/$P/assets3d.tar -C <WS> assets3d` in Git LFS so a fresh
  clone can restore them instead of re-rendering.

## Refreshing an existing project's toolkit
Compare first: `diff -rq "$T" pipeline/$P | grep -v examples`. Copy over only files the project has not changed
(`git log --oneline -- pipeline/$P/<file>`). For changed files, merge by hand and re-run the self-tests and one
still of each existing reel. Never overwrite project timelines, project.json, BRIEF*.md or BRAND.md.
