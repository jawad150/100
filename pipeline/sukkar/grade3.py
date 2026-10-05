"""Bake per-clip LUTs from the per-clip fits of the reference grade (look/fit3.json).

- clips with a reference: their own fitted grade
- other clips: the median look of the referenced OR shots, with a gentle automatic exposure
  (60% normalisation toward the referenced shots' graded level, capped at +/-0.9 stop;
   facility shots 40%, so they stay brighter and more open)
"""
import json
import os
import sys

import numpy as np

import fitlook3 as F3
import grade
import grade2 as G2

FIT = json.load(open("look/fit3.json"))
OR_REFS = ["C8893", "C8999", "C9019", "C9021"]
LOOK_KEYS = [k for k in F3.KEYS if k not in ("exposure", "wb_r", "wb_b")]


def median_look():
    return {k: float(np.median([FIT[c][k] for c in OR_REFS])) for k in LOOK_KEYS}


def graded_level():
    vals = [G2.median_log2_lin(c, G2.REF_TIMES[c]) + FIT[c]["exposure"] for c in OR_REFS]
    return float(np.mean(vals))


# clips without a reference borrow the full fitted grade of the most similar reference shot
DONOR = {"C9016": "C9021", "C9017": "C9021", "C9015": "C9021", "C9021": "C9021",
         "C8902": "C8893", "C8905": "C8893", "C8899": "C8893", "C8907": "C8893", "C8916": "C8893",
         "C8890": "C8893", "C8911": "C8893", "C8886": "C8893", "C8879": "C8893", "C8912": "C8893",
         "C9010": "C9019", "C9012": "C9019", "C8875": "C8999", "C8891": "C8999", "C8894": "C8999",
         "C8955": "C8893", "C8956": "C8893", "C9031": "C8893", "C9033": "C8893"}


def params_for(clip, times, target, look):
    if clip in FIT and clip not in ("C9021",):
        v = np.array([FIT[clip][k] for k in F3.KEYS])
        return F3.to_params(v), "fitted to reference"
    donor = DONOR.get(clip, "C8893")
    d = dict(FIT[donor])
    lvl = G2.median_log2_lin(clip, times)
    donor_lvl = G2.median_log2_lin(donor, G2.REF_TIMES[donor])
    k = 0.4 if clip in G2.FACILITY else 0.6
    e = float(np.clip(k * (donor_lvl - lvl), -0.9, 0.9))
    d["exposure"] = d["exposure"] + e
    v = np.array([d[k] for k in F3.KEYS])
    return F3.to_params(v), f"grade of {donor}, exposure match {e:+.2f}"


if __name__ == "__main__":
    clips = json.loads(sys.argv[1])
    look = median_look()
    target = graded_level()
    print("median OR look:", {k: round(v, 3) for k, v in look.items()})
    print(f"graded level target {target:.2f}")
    os.makedirs("luts3", exist_ok=True)
    for clip, ts in clips.items():
        p, how = params_for(clip, ts, target, look)
        grade.write_cube(f"luts3/{clip}.cube", p)
        print(f"{clip}: {how}")
