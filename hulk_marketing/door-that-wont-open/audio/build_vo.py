"""build_vo.py: cut the chosen ElevenLabs take into its 12 sentences and place each on the film's timeline.

    python3 audio/build_vo.py            (run from hulk_marketing/door-that-wont-open)

Reads  audio/vo_takes/takeA.wav (48 kHz mono) + takeA.words.json (Whisper word timings, verified word-perfect)
Writes audio/vo.wav (48 kHz stereo float, speech at about -16 LUFS integrated over the voiced parts)
       vo_words.json (every placed word: text, start, end in film seconds; the film times captions from it)
Line onsets are chosen in PLACE below; the cuts come from the take's own energy envelope (-40 dB re peak,
gaps under 0.12 s merged), trimmed 30 ms before / 120 ms after the speech and faded 10 / 60 ms.
"""
import json
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FILM, '..', '..', 'pipeline', 'fostering'))
import audio as A  # noqa: E402  (BS.1770 loudness from the repo's SFX library)

SR = 48000
DUR = json.load(open(os.path.join(FILM, 'film.json')))['duration']

# (line id, text, film time of the speech onset)
PLACE = [
    ('l1a', 'She found you.', 0.40),
    ('l1b', 'She wants to buy.', 1.70),
    ('l2', "But the door won't open.", 4.30),
    ('l3a', 'One second.', 9.00),
    ('l3b', 'Two.', 10.00),
    ('l3c', 'Three.', 11.00),
    ('l4', 'So she walks across the road.', 13.20),
    ('l5', "That's a slow website.", 18.50),
    ('l6', 'Every second of load time quietly costs you conversions.', 21.35),
    ('l7', 'We build sites that are fast, stable and easy to grow.', 26.10),
    ('l8a', 'See your opportunity in thirty seconds.', 31.10),
    ('l8b', 'Get your free website audit.', 33.75),
]
PRE, POST = 0.03, 0.12


def segments(a):
    hop = int(SR * 0.01)
    e = np.array([np.sqrt((a[i:i + hop] ** 2).mean()) for i in range(0, len(a) - hop, hop)])
    db = 20 * np.log10(e + 1e-9)
    on = db > db.max() - 40
    segs, start = [], None
    for i, v in enumerate(on):
        if v and start is None:
            start = i
        if not v and start is not None:
            segs.append([start, i])
            start = None
    if start is not None:
        segs.append([start, len(on)])
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < 12:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return [(s[0] / 100, s[1] / 100) for s in merged if s[1] - s[0] > 4]


def main():
    a, sr = sf.read(os.path.join(HERE, 'vo_takes', 'takeA.wav'), dtype='float64')
    assert sr == SR
    words = json.load(open(os.path.join(HERE, 'vo_takes', 'takeA.words.json')))
    segs = segments(a)
    assert len(segs) == len(PLACE), f'{len(segs)} segments, expected {len(PLACE)}'
    out = np.zeros(int(DUR * SR))
    placed, prev_end = [], -1
    for (lid, text, t0), (s0, s1) in zip(PLACE, segs):
        c0, c1 = max(0, s0 - PRE), min(len(a) / SR, s1 + POST)
        clip = a[int(c0 * SR):int(c1 * SR)].copy()
        fi, fo = int(0.01 * SR), int(0.06 * SR)
        clip[:fi] *= np.linspace(0, 1, fi)
        clip[-fo:] *= np.linspace(1, 0, fo)
        start = t0 - (s0 - c0)
        i0 = int(round(start * SR))
        out[i0:i0 + len(clip)] += clip
        shift = t0 - s0
        # words whose midpoint falls inside this segment (Whisper times are approximate; clamp to the segment)
        ws = [w for w in words if s0 - 0.25 <= (w['s'] + w['e']) / 2 <= s1 + 0.25]
        for w in ws:
            placed.append(dict(line=lid, w=w['w'], s=round(max(w['s'], s0) + shift, 3),
                               e=round(min(w['e'], s1) + shift, 3)))
        end = s1 + shift
        print(f'{lid:4s} {t0:6.2f}-{end:6.2f}  ({s1 - s0:4.2f} s)  gap {t0 - prev_end:5.2f}  {text}')
        assert t0 > prev_end, f'{lid} overlaps the previous line'
        prev_end = end
    # level: speech at -16 LUFS (the PDF's voice level), measured on the voiced parts only
    st = np.stack([out, out], 1)
    voiced = np.concatenate([st[int((p[2] - 0.03) * SR):int((p[2] + (s1 - s0) + 0.1) * SR)]
                             for p, (s0, s1) in zip(PLACE, segs)])
    g = 10 ** ((-16.0 - A.loudness(voiced.astype(np.float32))) / 20)
    st *= g
    print(f'gain {20 * np.log10(g):+.1f} dB, peak {20 * np.log10(np.abs(st).max()):.1f} dBFS')
    sf.write(os.path.join(HERE, 'vo.wav'), st.astype(np.float32), SR, subtype='FLOAT')
    json.dump(dict(lines=[dict(id=l, text=t, t=t0) for l, t, t0 in PLACE], words=placed),
              open(os.path.join(FILM, 'vo_words.json'), 'w'), indent=1)
    print('-> audio/vo.wav, vo_words.json')


if __name__ == '__main__':
    main()
