"""Dialogue bites: exact source ranges, pause tightening, splice points.

Times are in the source file's own clock. Interview bites (1-3) use the vertical
export's audio (better audio); the horizontal picture is at vertical + 2.9645 s.
"""
import json
import subprocess

import numpy as np

V = "src/C8950 V2 (1).mp4"
C = "src/C8951.MP4"
H = "src/C8948 (1).mov"
H_MINUS_V = 2.9645
SR = 48000
A = json.load(open("tx/aligned.json"))


def _load(path, t0, dur):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-ss", f"{t0:.4f}", "-t", f"{dur:.4f}", "-i", path,
                          "-map", "0:a:0", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


ANCHOR = {"b1": "BUT", "b2": "I", "b3": "BUT", "b4": "BUT", "b56": "THAT"}


def w(bite, word, nth=0):
    """nth occurrence of `word` counted from the bite's anchor word onward."""
    words = A[bite]
    start = next(i for i, x in enumerate(words) if x[0] == ANCHOR[bite])
    hits = [x for x in words[start:] if x[0] == word.upper()]
    return hits[nth]


def quiet_point(path, a, b, win=0.004):
    x = _load(path, a, b - a)
    n = int(win * SR)
    e = np.convolve(x * x, np.ones(n) / n, mode="same")
    i = int(np.argmin(e[n:-n])) + n if len(e) > 2 * n else len(e) // 2
    return a + i / SR


def speech_edges(path, a, b, hop=0.005):
    """Within a pause [a,b] (CTC end of prev word .. CTC start of next), find where the
    previous word's sound really stops and where the next word's sound starts."""
    x = _load(path, a - 0.05, (b - a) + 0.1)
    n = int(hop * SR)
    k = len(x) // n
    db = 10 * np.log10((x[:k * n].reshape(k, n) ** 2).mean(1) + 1e-12)
    floor = np.percentile(db, 10)
    thr = floor + 6
    ts = a - 0.05 + (np.arange(k) + 0.5) * hop
    quiet = db < thr
    # first run of >=4 quiet frames after a, last run before b
    end_prev, start_next = a, b
    run = 0
    for i in range(k):
        run = run + 1 if quiet[i] and ts[i] >= a - 0.02 else 0
        if run >= 4:
            end_prev = ts[i - 3]
            break
    run = 0
    for i in range(k - 1, -1, -1):
        run = run + 1 if quiet[i] and ts[i] <= b + 0.02 else 0
        if run >= 4:
            start_next = ts[i + 3]
            break
    if start_next <= end_prev:
        mid = (a + b) / 2
        return mid, mid
    return end_prev, start_next


def tighten(path, prev_end_ctc, next_start_ctc, target):
    """Return (cut_out, cut_in): play up to cut_out, then resume at cut_in, leaving about
    `target` seconds of pause (room tone) between the words."""
    e, s = speech_edges(path, prev_end_ctc, next_start_ctc)
    gap = s - e
    if gap <= target + 0.04:
        return None
    keep = target / 2
    return e + keep, s - keep


def build():
    """Bite definitions -> list of pieces [(path, t_in, t_out)] per bite (source times)."""
    bites = {}

    # ---- B1 (vertical): "to see the cornea restore someone's sight, and I helped be a part of that"
    b1_in = quiet_point(V, w("b1", "neat")[2] - 0.01, w("b1", "to")[1] + 0.01)
    b1_out = quiet_point(V, w("b1", "that")[2], w("b1", "so")[1] + 0.01)
    p = [(V, b1_in, None)]
    for (pw, pn), (nw, nn), tgt in [(("see", 0), ("the", 0), 0.26), (("sight", 0), ("and", 0), 0.42),
                                    (("helped", 0), ("be", 0), 0.16)]:
        r = tighten(V, w("b1", pw, pn)[2], w("b1", nw, nn)[1], tgt)
        if r:
            p[-1] = (V, p[-1][1], r[0])
            p.append((V, r[1], None))
    p[-1] = (V, p[-1][1], b1_out)
    bites["b1"] = p

    # ---- B2a (vertical): "I think | the craft of plastic surgery, it's boundless"
    think1_end = quiet_point(V, w("b2", "think", 0)[2] - 0.01, w("b2", "you")[1])
    craft_in = quiet_point(V, w("b2", "think", 1)[2] - 0.01, w("b2", "the")[1] + 0.005)
    i_start = w("b2", "i", 0)[1] - 0.08
    boundless_end, _ = speech_edges(V, w("b2", "boundless")[2], w("b2", "you're")[1])
    p = [(V, i_start, think1_end), (V, craft_in, None)]
    r = tighten(V, w("b2", "of")[2], w("b2", "plastic")[1], 0.14)
    p[-1] = (V, craft_in, r[0])
    p.append((V, r[1], boundless_end + 0.12))
    bites["b2a"] = p

    # ---- B2b (vertical): "You're always getting better"
    _, youre_start = speech_edges(V, w("b2", "boundless")[2], w("b2", "you're")[1])
    better_end = w("b2", "better")[2] + 0.085
    bites["b2b"] = [(V, youre_start - 0.10, better_end)]

    # ---- B3 (vertical): "We're always still learning and chasing perfection"
    were_in = quiet_point(V, w("b3", "but")[2] - 0.01, w("b3", "we're")[1] + 0.005)
    perf_out = quiet_point(V, w("b3", "perfection")[2], w("b3", "and", 1)[1] + 0.005)
    p = [(V, were_in, None)]
    for (pw, pn), (nw, nn), tgt in [(("learning", 0), ("and", 0), 0.30), (("and", 0), ("chasing", 0), 0.14)]:
        r = tighten(V, w("b3", pw, pn)[2], w("b3", nw, nn)[1], tgt)
        if r:
            p[-1] = (V, p[-1][1], r[0])
            p.append((V, r[1], None))
    p[-1] = (V, p[-1][1], perf_out)
    bites["b3"] = p

    # ---- B4 (C8951): "What we've created here is a wonderful experience ... for their patients"
    what_in = quiet_point(C, w("b4", "think")[2] - 0.01, w("b4", "what")[1] + 0.005)
    pat_end, _ = speech_edges(C, w("b4", "patients")[2], w("b4", "because")[1])
    p = [(C, what_in, None)]
    for (pw, pn), (nw, nn), tgt in [(("here", 0), ("is", 0), 0.22), (("is", 0), ("a", 0), 0.12),
                                    (("here", 1), ("as", 0), 0.34), (("are", 0), ("coming", 0), 0.18),
                                    (("which", 0), ("they", 0), 0.20)]:
        r = tighten(C, w("b4", pw, pn)[2], w("b4", nw, nn)[1], tgt)
        if r:
            p[-1] = (C, p[-1][1], r[0])
            p.append((C, r[1], None))
    p[-1] = (C, p[-1][1], pat_end + 0.10)
    bites["b4"] = p

    # ---- B5 (C8951): "Actually, I'd like to say that going to surgery is like a spa day for me"
    _, actually_start = speech_edges(C, w("b56", "that")[2], w("b56", "actually")[1])
    me_because = quiet_point(C, w("b56", "me")[2] + 0.06, w("b56", "because")[1] + 0.03)
    p = [(C, actually_start - 0.06, None)]
    r = tighten(C, w("b56", "i'd")[2], w("b56", "like")[1], 0.12)
    if r:
        p[-1] = (C, p[-1][1], r[0])
        p.append((C, r[1], None))
    p[-1] = (C, p[-1][1], me_because)
    bites["b5"] = p

    # ---- B6 (C8951): "because when I'm in surgery, I'm in control"
    control_end, _ = speech_edges(C, w("b56", "control")[2], w("b56", "and", 0)[1])
    p = [(C, me_because, None)]
    r = tighten(C, w("b56", "surgery", 1)[2], w("b56", "i'm", 1)[1], 0.46)
    if r:
        p[-1] = (C, me_because, r[0])
        p.append((C, r[1], None))
    p[-1] = (C, p[-1][1], control_end + 0.15)
    bites["b6"] = p
    return bites


if __name__ == "__main__":
    b = build()
    tot = 0
    for k, pieces in b.items():
        d = sum(o - i for _, i, o in pieces)
        tot += d
        print(f"{k}: {d:5.2f}s  " + "  ".join(f"[{i:.3f}-{o:.3f}]" for _, i, o in pieces))
    print(f"total dialogue {tot:.2f}s")
    json.dump(b, open("tx/bites.json", "w"), indent=1)
