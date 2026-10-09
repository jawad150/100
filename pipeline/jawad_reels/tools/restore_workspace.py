"""Restore the git-ignored workspace from the committed brand_reels/assets/ (RESUME.md "Restore a fresh container").

    python3 pipeline/jawad_reels/tools/restore_workspace.py          (idempotent; run after setup_workspace.py)

brand_reels/assets/<slug>/vo_raw/*            -> workspace/jawad_reels/<slug>/vo/raw/
brand_reels/assets/<slug>/vo_final/*.flac     -> workspace/jawad_reels/<slug>/vo/*.wav   (pcm_s24le)
brand_reels/assets/<slug>/**.json (top+final) -> workspace/jawad_reels/<slug>/vo/
brand_reels/assets/<slug>/props|assets3d      -> workspace/jawad_reels/<slug>/props|assets3d  (+ the alias symlink)
brand_reels/assets/charsheet/cutouts          -> workspace/brand_reels/charsheet/cutouts
brand_reels/assets/charsheet/faces.py         -> workspace/brand_reels/charsheet/tools/faces.py
(derived)                                     -> workspace/brand_reels/charsheet/crops/ (tools/rebuild_crops.py)
"""
import glob
import os
import shutil
import subprocess

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
A = os.path.join(REPO, 'brand_reels', 'assets')
WJ = os.path.join(REPO, 'workspace', 'jawad_reels')
WB = os.path.join(REPO, 'workspace', 'brand_reels')


def copytree(src, dst):
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)


def main():
    for d in sorted(glob.glob(os.path.join(A, '*'))):
        slug = os.path.basename(d)
        if slug == 'charsheet' or not os.path.isdir(d):
            continue
        vo = os.path.join(WJ, slug, 'vo')
        os.makedirs(vo, exist_ok=True)
        copytree(os.path.join(d, 'vo_raw'), os.path.join(vo, 'raw'))
        for j in glob.glob(os.path.join(d, '*.json')) + glob.glob(os.path.join(d, 'vo_final', '*.json')):
            shutil.copy2(j, vo)
        for f in glob.glob(os.path.join(d, 'vo_final', '*.flac')):
            out = os.path.join(vo, os.path.basename(f)[:-5] + '.wav')
            if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(f):
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-c:a', 'pcm_s24le', out], check=True)
        for sub in ('props', 'assets3d'):
            copytree(os.path.join(d, sub), os.path.join(WJ, slug, sub))
        # the builders load through the other name (assets3d_<slug>.py: props <-> assets3d alias)
        for have, alias in (('assets3d', 'props'), ('props', 'assets3d')):
            p, q = os.path.join(WJ, slug, have), os.path.join(WJ, slug, alias)
            if os.path.isdir(p) and not os.path.lexists(q):
                os.symlink(have, q)
        print('%-24s vo %d wav, %d raw' % (slug, len(glob.glob(vo + '/*.wav')), len(glob.glob(vo + '/raw/*'))))
    copytree(os.path.join(A, 'charsheet', 'cutouts'), os.path.join(WB, 'charsheet', 'cutouts'))
    os.makedirs(os.path.join(WB, 'charsheet', 'tools'), exist_ok=True)
    shutil.copy2(os.path.join(A, 'charsheet', 'faces.py'), os.path.join(WB, 'charsheet', 'tools', 'faces.py'))
    print('charsheet: %d cut-out files' % len(os.listdir(os.path.join(WB, 'charsheet', 'cutouts'))))
    subprocess.run(['python3', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rebuild_crops.py')], check=True)


if __name__ == '__main__':
    main()
