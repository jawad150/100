"""QA helpers: labeled contact sheets of rendered frames + a caption table.

python3 qa_sheets.py [step]  -> $WS/qa/sheet_XX.jpg (every `step`-th frame), $WS/qa/captions.txt
"""
import os, sys
import numpy as np, cv2
from common import WS, FPS, NFRAMES, CUTS
import render as R

step = int(sys.argv[1]) if len(sys.argv) > 1 else 2
out = f'{WS}/qa'
os.makedirs(out, exist_ok=True)
fis = list(range(0, NFRAMES, step))
per = 24  # frames per sheet (6 x 4)
for si in range(0, len(fis), per):
    tiles = []
    for fi in fis[si:si + per]:
        im = cv2.imread(f'{WS}/out/frames/{fi:04d}.png')
        im = cv2.resize(im, (270, 480), interpolation=cv2.INTER_AREA)
        lab = f'{fi} {fi / FPS:.2f}s' + (' CUT' if fi in CUTS else '')
        cv2.rectangle(im, (0, 0), (270, 26), (0, 0, 0), -1)
        cv2.putText(im, lab, (6, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        tiles.append(im)
    while len(tiles) % 6:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.concatenate(tiles[i:i + 6], 1) for i in range(0, len(tiles), 6)]
    cv2.imwrite(f'{out}/sheet_{si // per:02d}.jpg', np.concatenate(rows, 0), [cv2.IMWRITE_JPEG_QUALITY, 88])

lines = ['TRANSCRIPT (word: start-end s)']
lines.append(' '.join(f"{w['w']}[{w['s']:.2f}-{w['e']:.2f}]" for w in R.WORDS))
lines.append('\nCUTS (frame / seconds): ' + ', '.join(f'{c}/{c / FPS:.2f}' for c in CUTS))
lines.append('\nTRANSITIONS: ' + ', '.join(f'{c}:{t}' for c, t in R.TRANS.items()))
lines.append('\nON-SCREEN TEXT (overlay = front, screen-space; scene = big word in the plate, behind her)')
for el in R.OVERLAY:
    if el['kind'] in ('cap', 'l1', 'l3', 'strike_cap'):
        lines.append(f"overlay {el['kind']:10s} '{' '.join(el['words'])}' words@{[round(x, 2) for x in el['times']]} end {el['end']:.2f}")
    elif el['kind'] == 'pill':
        lines.append(f"overlay pill       '{el['text']}' {el['t0']:.2f}-{el['end']:.2f}")
for k, els in R.SCENE.items():
    for el in els:
        if el['kind'] == 'l2':
            lines.append(f"scene   shot {k:2d} big '{el['text']}' {el['color']} {el['t0']:.2f}-{min(el['end'], 40.5):.2f} behind={el['behind']}")
        else:
            lines.append(f"scene   shot {k:2d} photo cards 15.35-20.80 + glow line {R.LINE_T}")
open(f'{out}/captions.txt', 'w').write('\n'.join(lines) + '\n')
print('sheets', (len(fis) + per - 1) // per, 'captions', f'{out}/captions.txt')
