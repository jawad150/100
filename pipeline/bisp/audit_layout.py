"""Layout audit: render every 0.1 s and check each drawn panel and the captions against (1) the protected zone
around the presenter (hair, face, neck; facetrack.py, sampled every 0.2 s) and (2) the Instagram Reels safe area.
The logo pill is checked against the safe area only (it is fixed branding at the very top). Prints every violation.

    python3 audit_layout.py [step=0.1]
"""
import os, sys, json
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def face_at(F, seg, t):
    """The protected zone (hair, face, neck) at time t; the segment's whole-zone union when no sample is near."""
    tr = F[seg].get('ztrack') or F[seg]['track']
    if tr:
        r = min(tr, key=lambda x: abs(x[0] - t))
        if abs(r[0] - t) < 0.3:
            return r[1:]
    return F[seg].get('zone')


def check(t):
    import reel
    reel.render_frame(t)
    seg = reel.TL.seg_at(t)['id'] if t < reel.TL.speech_end else None
    out = []
    for tag, x0, y0, x1, y1 in reel.RECTS:
        if tag in ('endcard',) or (t >= reel.PLAN['end_in'] and tag == 'logo'):
            continue
        if seg and tag != 'logo':
            fb = face_at(reel.FSEG, seg, t)
            if fb:
                ix = min(x1, fb[2]) - max(x0, fb[0]); iy = min(y1, fb[3]) - max(y0, fb[1])
                if ix > 2 and iy > 2:
                    out.append(f'{t:7.2f} {seg:9s} ZONE  {tag:8s} panel y {y0:.0f}-{y1:.0f} x {x0:.0f}-{x1:.0f}  zone y {fb[1]:.0f}-{fb[3]:.0f} (overlap {iy:.0f}px)')
        S = reel.SAFE
        if x0 < S['l'] - 1 or x1 > S['r'] + 1 or y0 < S['top'] - 1 or y1 > S['bot'] + 1:
            out.append(f'{t:7.2f} {str(seg):9s} SAFE  {tag:8s} x {x0:.0f}-{x1:.0f} y {y0:.0f}-{y1:.0f}')
    return out


if __name__ == '__main__':
    import edl
    step = float(sys.argv[1]) if len(sys.argv) > 1 else 0.1
    ts = [round(i * step, 3) for i in range(int(edl.timeline().dur / step))]
    with Pool(4) as p:
        res = p.map(check, ts, chunksize=8)
    bad = [x for r in res for x in r]
    for x in bad: print(x)
    print('frames checked', len(ts), 'violations', len(bad))
