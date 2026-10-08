"""wsconf.py - where this toolkit keeps its data, and the optional per-project overrides (project.json).

Every toolkit module resolves its workspace through workspace(): FOSTER_WS env > "workspace" in
project.json (relative to the repo root) > <repo>/workspace3. Without a project.json nothing changes.

project.json sits next to this file (pipeline/<project>/project.json) and is written per client, e.g.
    {"project": "acme", "workspace": "workspace_acme",
     "palette": {"MAGENTA": "#1E40AF", "ORANGE": "#F59E0B", "INK": "#0F172A", "IVORY": "#F8FAFC"},
     "font_map": {"Nunito": "Inter", "Poppins": "Manrope", "Caveat": "Kalam"}}
"palette" overrides core.PALETTE_HEX by key (the keys are colour roles; see TOOLKIT.md), and "font_map"
renames font families in core.font_path ('Nunito-Black' -> 'Inter-Black.ttf').
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
_cache = {}


def project():
    """project.json next to this file as a dict ({} when absent).  e.g. project().get('palette', {})"""
    if 'p' not in _cache:
        p = os.path.join(HERE, 'project.json')
        _cache['p'] = json.load(open(p)) if os.path.exists(p) else {}
    return _cache['p']


def workspace():
    """Absolute workspace folder.  e.g. workspace() -> '/repo/workspace3'"""
    env = os.environ.get('FOSTER_WS')
    if env:
        return os.path.abspath(env)
    return os.path.abspath(os.path.join(REPO, project().get('workspace', 'workspace3')))


def font_name(name):
    """Apply project.json "font_map" to a font basename.  e.g. font_name('Nunito-Black') -> 'Inter-Black'"""
    fam, sep, rest = name.partition('-')
    new = project().get('font_map', {}).get(fam)
    return new + sep + rest if new else name
