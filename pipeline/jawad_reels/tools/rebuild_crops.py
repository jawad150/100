"""Rebuild workspace/brand_reels/charsheet/crops/ from the committed cut-outs (session 3, 2026-10-09).

The original crops (native sheet crop <name>.png + Real-ESRGAN 2x master <name>_2x.png) lived only in the git-ignored
workspace together with the two character sheets, and both were lost between sessions. The face modules use them for
one thing: the skin-only SR detail pull-back  rgb = lanczos2x(native) + k * (sr2x - lanczos2x(native))  (TEX_K).

Reconstruction (documented approximation, not bit-exact):
    <name>_2x.png = the cut-out's RGB (the cut-out IS the 2x SR master after matting; the pull-back only touches the
                    eroded alpha > 0.99 core, where the matte did not change the colours)
    <name>.png    = INTER_AREA 2x downscale of that RGB back to native_wh (keeps the content below the native Nyquist
                    limit, so sr2x - lanczos2x(native) is the detail Real-ESRGAN added above it: the pull-back target)
Outside the subject the RGB is the matte's foreground estimate, which the eroded/blurred core weight never reaches.

    python3 pipeline/jawad_reels/tools/rebuild_crops.py      (idempotent; restore_workspace.py calls it)
"""
import glob
import json
import os

import cv2

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
CUT = os.path.join(REPO, 'brand_reels', 'assets', 'charsheet', 'cutouts')
OUT = os.path.join(REPO, 'workspace', 'brand_reels', 'charsheet', 'crops')


def main():
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for js in sorted(glob.glob(os.path.join(CUT, '*.json'))):
        name = os.path.basename(js)[:-5]
        meta = json.load(open(js))
        cut = cv2.imread(os.path.join(CUT, name + '.png'), cv2.IMREAD_UNCHANGED)
        if cut is None or cut.ndim != 3 or cut.shape[2] != 4:
            continue
        rgb = cut[..., :3]
        nw, nh = meta.get('native_wh') or (cut.shape[1] // 2, cut.shape[0] // 2)
        cv2.imwrite(os.path.join(OUT, name + '_2x.png'), rgb)
        cv2.imwrite(os.path.join(OUT, name + '.png'), cv2.resize(rgb, (int(nw), int(nh)), interpolation=cv2.INTER_AREA))
        n += 1
    print('crops ->', OUT, n, 'poses (reconstructed from cut-outs)')


if __name__ == '__main__':
    main()
