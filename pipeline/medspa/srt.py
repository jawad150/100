"""Write the spoken words as an .srt (phrases of up to ~5 words, split on punctuation/pauses)."""
import json, os, sys
from common import HERE
import render as R

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'reel', 'medspa', 'PS_MedSpa_Reel.srt')
ws = R.WORDS
phr, cur = [], []
for i, w in enumerate(ws):
    cur.append(i)
    gap = ws[i + 1]['s'] - w['e'] if i + 1 < len(ws) else 9
    if w['w'][-1] == '.' or (w['w'][-1] == ',' and len(cur) >= 3) or len(cur) >= 6 or gap > 0.35:
        phr.append(cur)
        cur = []
if cur:
    phr.append(cur)
merged = []
for p in phr:
    if merged and len(p) == 1 and len(merged[-1]) < 7:
        merged[-1] = merged[-1] + p
    else:
        merged.append(p)
phr = merged

def ts(t):
    ms = int(round(t * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'

lines = []
for n, p in enumerate(phr, 1):
    a = ws[p[0]]['s']
    b = min(ws[p[-1]]['e'] + 0.25, ws[p[-1] + 1]['s'] if p[-1] + 1 < len(ws) else 99)
    lines += [str(n), f'{ts(a)} --> {ts(b)}', ' '.join(R.wd(i) for i in p).replace(' & ', ' and '), '']
open(out, 'w').write('\n'.join(lines))
print('wrote', out, len(phr), 'cues')
