"""vo_prep.py - turn the ElevenLabs takes in media/oktrum/vo/ into edit-ready VO stems + phrase timings.

    python3 vo_prep.py            # all reels, voice A
    python3 vo_prep.py --voice B  # the alternative voice

For each reel: decode the take (48 kHz mono float), find the spoken phrases (energy gate), tighten pauses longer
than CAP to CAP (the hook pauses keep their rhythm), add a gentle high-pass, de-ess-free presence lift and a soft
compressor, place the VO at OFFSET s in the edit and normalise to -16 LUFS (true peak <= -3 dBTP before the music
mix). Writes <WS>/audio/reelN_vo.wav and <WS>/audio/reelN_vo.json:
    {"offset": .., "dur": .., "phrases": [{"text": .., "t0": .., "t1": ..}, ...]}
Phrase t0/t1 are edit times (s). Timeline builders pin each on-screen key word to its phrase.
"""
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wsconf  # noqa: E402

SR = 48000
VO_DIR = os.path.join(wsconf.REPO, 'media', 'oktrum', 'vo')
OUT = os.path.join(wsconf.workspace(), 'audio')
OFFSET = 0.20
CAP = 0.34

# phrase texts in spoken order (must match the energy-gated segments of voice A; B is checked by count)
PHRASES = {
    1: ['Forex.', 'Gold.', 'Bitcoin.', 'Nvidia.', 'All on one platform.',
        'Trade forex, commodities, stocks, indices and crypto on MetaTrader 5.', 'Spreads from zero point two pips.',
        'Zero hidden fees.', 'Oktrum.', 'Trade the global markets with precision.', 'Try a free demo today.'],
    2: ['Blink...', 'and the price has already moved.', 'In trading,', 'every millisecond counts.',
        'Oktrum runs on ultra-low-latency servers for instant order filling,', 'on MetaTrader 5.', 'Eliminate lag,',
        'and seize every market opportunity.', 'Open your live account at oktrum dot com.'],
    3: ['What happens if the market crashes overnight?', 'With Oktrum,', 'your account can never go below zero.',
        "That's negative balance protection,", 'plus bank-tier encryption', 'and expert support.',
        'Trade with total peace of mind.', 'Oktrum.', 'Trade with confidence.', 'Get started at oktrum dot com.'],
}
# gaps (index of the phrase BEFORE the gap) that keep their natural length: hook rhythm
KEEP = {1: {0, 1, 2}, 2: {0}, 3: set()}


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def segments(x, gap_merge=0.17, floor_db=38.0):
    hop = SR // 100
    e = np.sqrt(np.convolve(x.astype(np.float64) ** 2, np.ones(1200) / 1200, 'same'))[::hop]
    db = 20 * np.log10(e + 1e-7)
    on = db > db.max() - floor_db
    segs, i, n = [], 0, len(on)
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            segs.append([i * hop / SR, j * hop / SR])
            i = j
        else:
            i += 1
    out = []
    for s in segs:
        if out and s[0] - out[-1][1] < gap_merge:
            out[-1][1] = s[1]
        else:
            out.append(s)
    return [s for s in out if s[1] - s[0] > 0.06]


def biquad(x, b, a):
    from scipy.signal import lfilter
    return lfilter(b, a, x).astype(np.float32)


def tone(x):
    from scipy.signal import butter
    b, a = butter(2, 80 / (SR / 2), 'highpass')
    x = biquad(x, b, a)
    # presence lift: add a band around 3-5 kHz
    b, a = butter(2, [3000 / (SR / 2), 5200 / (SR / 2)], 'bandpass')
    x = x + 0.22 * biquad(x, b, a)
    # soft compressor (RMS, 3:1 above -20 dBFS, 8 ms / 120 ms)
    env = np.sqrt(np.convolve(x.astype(np.float64) ** 2, np.ones(480) / 480, 'same'))
    db = 20 * np.log10(env + 1e-9)
    gr = np.where(db > -20, (db + 20) * (1 - 1 / 3.0), 0.0)
    g = 10 ** (-gr / 20)
    # smooth the gain (release)
    from scipy.signal import lfilter
    g = lfilter([0.02], [1, -0.98], g)
    return (x * g).astype(np.float32)


def loudness_norm(x, target=-16.0, tp=-3.0):
    import pyloudnorm as pyln
    m = pyln.Meter(SR)
    lufs = m.integrated_loudness(x.astype(np.float64))
    y = x * 10 ** ((target - lufs) / 20)
    up = np.abs(np.interp(np.arange(len(y) * 4) / 4, np.arange(len(y)), y)).max()
    lim = 10 ** (tp / 20)
    if up > lim:
        y = y * lim / up
    return y.astype(np.float32), lufs


def build(reel, voice='A'):
    src = os.path.join(VO_DIR, f'reel{reel}_{voice}.mp3')
    x = load(src)
    segs = segments(x)
    names = PHRASES[reel]
    if len(segs) != len(names):
        raise SystemExit(f'reel{reel}_{voice}: {len(segs)} segments, expected {len(names)}: {segs}')
    pad = 0.06
    phrases, t = [], OFFSET
    out_parts = [np.zeros(int(OFFSET * SR), np.float32)]
    for k, (s0, s1) in enumerate(segs):
        a, b = max(0.0, s0 - pad), min(len(x) / SR, s1 + pad)
        if k + 1 < len(segs):
            gap = segs[k + 1][0] - s1
            keep = gap if (k in KEEP[reel] or gap <= CAP) else CAP
            b = min(b, s1 + keep / 2)
        seg = x[int(a * SR):int(b * SR)].copy()
        f = int(0.012 * SR)
        seg[:f] *= np.linspace(0, 1, f)
        seg[-f:] *= np.linspace(1, 0, f)
        t0 = t + (s0 - a)
        phrases.append(dict(text=names[k], t0=round(t0, 3), t1=round(t0 + (s1 - s0), 3)))
        out_parts.append(seg)
        t += len(seg) / SR
        if k + 1 < len(segs):
            # silence so that the next phrase onset lands `keep` after this one's end
            gap_fill = phrases[-1]['t1'] + keep - pad - t
            if gap_fill > 0:
                out_parts.append(np.zeros(int(gap_fill * SR), np.float32))
                t += int(gap_fill * SR) / SR
    y = np.concatenate(out_parts)
    y = tone(y)
    y, lufs_in = loudness_norm(y)
    os.makedirs(OUT, exist_ok=True)
    import soundfile as sf
    wav = os.path.join(OUT, f'reel{reel}_vo.wav')
    sf.write(wav, y, SR, subtype='PCM_24')
    meta = dict(source=os.path.relpath(src, wsconf.REPO), voice=voice, offset=OFFSET, cap=CAP,
                dur=round(len(y) / SR, 3), vo_end=phrases[-1]['t1'], phrases=phrases)
    json.dump(meta, open(os.path.join(OUT, f'reel{reel}_vo.json'), 'w'), indent=1)
    # also keep the timing next to the code so builders without the workspace can read it
    json.dump(meta, open(os.path.join(HERE, f'reel{reel}_vo.json'), 'w'), indent=1)
    print(f'reel{reel}: {meta["dur"]:.2f} s, VO ends {meta["vo_end"]:.2f} s ->', wav)
    for p in phrases:
        print(f'   {p["t0"]:6.2f}-{p["t1"]:6.2f}  {p["text"]}')
    return meta


if __name__ == '__main__':
    v = sys.argv[sys.argv.index('--voice') + 1] if '--voice' in sys.argv else 'A'
    for r in (1, 2, 3):
        build(r, v)
