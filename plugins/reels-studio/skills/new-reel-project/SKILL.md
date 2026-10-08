---
description: Scaffolds a new client motion-reel project in the current repository from the reels-studio toolkit. It copies the Python motion toolkit (3D compositor, type, SaaS UI kit, footage, Blender prop builders, SFX library, renderer, packager) into pipeline/<project>/, writes project.json (workspace folder, brand palette roles, font map, site, Drive footage folder, delivery folder), sets up .gitignore and Git LFS for masters, archives and footage, checks the Python, Blender and ffmpeg dependencies, builds the brand kit and workspace, runs the self-tests and a smoke render, and hands over to the creative director for the brief.
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
- Audio policy: SFX only, SFX + music (licence; credit ceiling for AI music), or voice-over. Captions: yes or no.
  Paid ads: yes or no.
- Reference reels the client likes.

## 2. Copy the toolkit
```bash
P=<project-slug>; T="${CLAUDE_PLUGIN_ROOT}/toolkit"
[ -d "$T" ] || T=$(dirname "$(find ~/.claude/plugins -name wsconf.py -path '*reels-studio*toolkit*' | head -1)")
mkdir -p pipeline/$P && cp -n "$T"/*.py "$T"/TOOLKIT.md pipeline/$P/ && cp -rn "$T"/examples pipeline/$P/
ls pipeline/$P
```
`cp -n` never overwrites. Only code and TOOLKIT.md are copied, never example briefs. `examples/` holds finished
timelines from earlier projects (reels, animations, `reel_demo.py`, `demo_looks.py`): read them for patterns,
never render them in a new project, because their copy, footage and brand belong to another client.
`$T/LOCAL_SETUP.md` and `$T/bootstrap_wsl.sh` describe the original project's PC setup (its paths, footage and props
are hard-coded): use them as a reference for the generic steps, never run the script as-is.

## 3. project.json (committed)
Write `pipeline/$P/project.json`:
```json
{
  "project": "<slug>",
  "workspace": "workspace_<slug>",
  "site": "https://client.com",
  "site_images_regex": "<regex for the site's photo paths, e.g. images/[^\"]+\\.jpg>",
  "drive_folder": "<Drive folder id; REQUIRED before running --footage>",
  "google_fonts": {"Inter": "Inter:wght@400;500;600;700;800;900", "Kalam": "Kalam:wght@700"},
  "font_map": {"Nunito": "Inter", "Poppins": "Inter", "Caveat": "Kalam"},
  "logo_src": "pipeline/<slug>/brand_src/logo.svg",
  "logo_dark_lum": 0.12,
  "palette": {},
  "deliver": {"dir": "reel/<slug>", "prefix": "<slug>"}
}
```
- `workspace` is the git-ignored data folder (fonts, logos, footage frames, 3D renders, audio, renders), relative to
  the repo root. `FOSTER_WS=/path` overrides it for one shell.
- `palette`, `font_map`, `google_fonts`, `logo_src`, `logo_dark_lum` and `site` are filled in by the
  brand-kit-builder agent (step 6). The palette keys are colour roles (MAGENTA = primary, ORANGE = accent, LEAF =
  secondary, INK = dark text, IVORY = light, NIGHT_0/1 = darkest…). The `google_fonts` keys are the file prefixes
  that `font_map` points to; spec spaces are written `+`.
- `site`, `logo_src` and `google_fonts` are required: setup_workspace.py and package.py fall back to the toolkit's
  original client (its site, logo scrape, fonts, Drive footage and delivery folder) for any missing key.
- Run `setup_workspace.py --footage` only when `drive_folder` is set. With local footage or none, never run
  `--footage`: footage-editor extracts local clips with ffmpeg, and the files go into Git LFS (step 4).

## 4. Repository setup
```bash
for l in "workspace_$P/" '__pycache__/' '*.pyc'; do grep -qxF "$l" .gitignore 2>/dev/null || echo "$l" >> .gitignore; done
for l in "reel/$P/*_master.mp4" "media/$P/*.tar" "media/$P/footage/*" "media/$P/music/*"; do
  grep -qF "$l filter=lfs" .gitattributes 2>/dev/null || echo "$l filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
done
git lfs install --local 2>/dev/null || echo "install git-lfs (apt install git-lfs / brew install git-lfs)"
```
Both loops only append missing lines (never sort a .gitignore: it breaks `!negation` lines). Local source footage
goes to `media/$P/footage/` as soon as it arrives, so a reset container can restore it with `git lfs pull`.

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
- Windows/WSL2: clone into the Linux home folder (not `/mnt/c`), give WSL most of the RAM in
  `%UserProfile%\.wslconfig` (`[wsl2]` `memory=12GB`, then `wsl --shutdown`), and install the NVIDIA driver on
  Windows; `nvidia-smi` must work inside Ubuntu. `$T/LOCAL_SETUP.md` walks through these steps.
- An NVIDIA GPU makes 3D props about 10× faster: check `nvidia-smi`, then set `FOSTER_GPU=1` for the Blender builders.

## 6. Brand kit and workspace
1. Run the **reels-studio:brand-kit-builder** agent with the slug, site, logo files and content doc. It fills the
   brand keys of project.json, downloads the fonts and logos into the workspace, commits the logo source and crops in
   `pipeline/$P/brand_src/`, and writes `pipeline/$P/BRAND.md` with a restore block.
2. Then, in `pipeline/$P/`: `python3 setup_workspace.py` (fonts, logo, site photos from project.json) and the BRAND.md
   restore block; with a Drive folder, `python3 setup_workspace.py --footage` (→ `frames/cXX/%05d.jpg` +
   `manifest.json`). Re-run both after a fresh clone or a reset container; the workspace is never committed.
3. Verify (all True):
   `python3 -c "import os,core; p=core.font_path('Nunito-Black'); print(core.WS, core.PALETTE_HEX['MAGENTA'], p, os.path.exists(p)); [print(w, os.path.exists(core.font_path(w))) for w in ('Nunito-Black','Nunito-ExtraBold','Nunito-Bold','Poppins-Regular','Poppins-Medium','Poppins-SemiBold','Poppins-Bold','Caveat-Bold')]"`

## 7. Self-tests and smoke render
In `pipeline/$P/`, run `python3 <module>.py selftest` for core, type3d, ui and audio; sprites3d needs at least one
3D asset. `footage.py selftest` and `render.py selftest` read the original project's clips (c01, c10, c12, c13) and
`reel_demo`: run footage's only if those frames exist, otherwise check a clip with
`python3 -c "import footage as F; print(F.contact_sheet('c00', n=8))"`. Open the PNGs in `<WS>/out/selftest/`: the
type, glass UI and looks must show the new brand colours and fonts (extrude3d sides and bloom tint stay in the
toolkit's original colours until a profile overrides them; BRAND.md lists them). Then a smoke render with no client
data, footage or 3D assets: write `pipeline/$P/smoke.py`
```python
"""smoke.py - 2 s toolkit smoke test (background, type, glass window). Delete after the check."""
import functools
import core as K, type3d as T, ui
DUR, LOOK, BPM = 2.0, 'neon', 120

@functools.lru_cache(maxsize=1)
def assets():
    return dict(word=T.render('TEST', 'extrude3d', px=200),
                win=ui.app_window(w=760, h=560, look=LOOK, title='smoke test', header='Smoke test', sidebar=False))

def prewarm(): assets()

def draw(t):
    a = assets(); cv = K.background(LOOK, t)
    a['win'].draw(cv, K.CX, 1180); a['word'].draw(cv, K.CX, 640 + 60 * t)
    return cv

def post(cv, t): return K.post(cv, LOOK, t)
def samples(t): return 1
```
then `python3 render.py smoke --sheet 4 --samples 1 --workers 1` and Read `<WS>/out/smoke/sheet.jpg`.

## 8. Hand over
- Commit `pipeline/$P/` (code, project.json, BRAND.md, brand_src/), `.gitignore` and `.gitattributes`, then push.
- Next: reference-analyst (if the client shared references) and trend-researcher, then **creative-director** writes
  `pipeline/$P/BRIEF.md`. The reels-production-playbook skill has the full order of work.
- 3D props: blender-3d-artist renders only the assets the brief lists (`python3 assets3d_<set>.py <name>`), never
  `all`: the bundled builders' `all` targets are the original client's prop library (about 1.5 h of CPU). Archive
  finished renders with `tar -cf media/$P/assets3d.tar -C <WS> assets3d` in Git LFS so a fresh clone can restore
  them instead of re-rendering.

## Refreshing an existing project's toolkit
Compare first: `diff -rq "$T" pipeline/$P | grep -v examples`. Copy over only files the project has not changed
(`git log --oneline -- pipeline/$P/<file>`). For changed files, merge by hand and re-run the self-tests and one
still of each existing reel. Never overwrite project timelines, project.json, BRIEF*.md, BRAND.md or brand_src/.
