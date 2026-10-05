"""Bake per-clip LUTs with the look fitted to the client's reference grade (fitlook.py).

clip LUT = G( base(code; exposure_c, wb_c) )
 - clips that appear in the reference use the colorist's fitted trims
 - every other clip gets an automatic exposure match to the referenced OR shots
   (facility shots are only half-normalised so they stay brighter / more open)
"""
import json
import os
import subprocess
import sys

import numpy as np

import fitlook as F
import grade

FIT = np.load("look/fit.npz")
G = FIT["G"]
TRIMS = {str(n): FIT["trims"][i] for i, n in enumerate(FIT["names"])}
FACILITY = {"C8955", "C8956", "C9031", "C8842", "C8852", "C8853", "C8954", "C8962", "C8963", "C8965",
            "C8967", "C8972", "C8973", "C8976", "C8859"}


def clip_path(clip):
    for ext in (".MP4", ".mov"):
        p = f"clips/{clip}{ext}"
        if os.path.exists(p):
            return p
    raise FileNotFoundError(clip)


def median_log2_lin(clip, times):
    p = clip_path(clip)
    rng = "tv" if p.endswith(".mov") else "pc"
    vals = []
    for t in times:
        code = F.frame(p, t, rng)
        lin = grade.gamut_compress(grade.slog3_to_linear(code) @ grade.M_SG3C_TO_709.T)
        Y = lin @ grade.LUMA
        vals.append(np.log2(np.median(np.maximum(Y, 1e-4))))
    return float(np.mean(vals))


REF_TIMES = {"C8893": (26.5, 29.5, 32.5), "C8999": (22.8, 23.6, 24.4), "C9019": (14.8, 15.5, 16.3),
             "C9028": (2.3, 3.0, 4.0), "C9021": (17.8, 18.6, 19.4), "C8939": (6.6, 7.2, 7.6)}


def target_level():
    """Average 'graded exposure' of the referenced clips: log2(median linear) + their exposure trim."""
    vals = []
    for clip, ts in REF_TIMES.items():
        if clip in ("C8939",):          # a door sign: not representative of scene exposure
            continue
        vals.append(median_log2_lin(clip, ts) + float(TRIMS[clip][0]))
    return float(np.mean(vals))


def params_for(clip, sample_times, target):
    if clip in TRIMS:
        e, rg, bg = (float(v) for v in TRIMS[clip])
        return e, (2 ** rg, 1.0, 2 ** bg), "fitted"
    lvl = median_log2_lin(clip, sample_times)
    k = 0.5 if clip in FACILITY else 0.8
    e = float(np.clip(k * (target - lvl), -1.2, 1.2))
    return e, (1.0, 1.0, 1.0), "auto"


def look(code, e, wb):
    return np.clip(F.apply_G(G, F.base(code, e, wb)), 0, 1)


def write_cube(path, e, wb, n=65):
    g = np.linspace(0, 1, n, dtype=np.float32)
    b, gg, r = np.meshgrid(g, g, g, indexing="ij")
    code = np.stack([r, gg, b], -1).reshape(-1, 3)
    out = np.concatenate([look(code[i:i + 40000][None], e, wb)[0] for i in range(0, len(code), 40000)])
    with open(path, "w") as f:
        f.write(f'TITLE "sukkar-reference-match"\nLUT_3D_SIZE {n}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
        np.savetxt(f, out, fmt="%.6f")


if __name__ == "__main__":
    # clip -> a few representative source times (from the edit)
    clips = json.loads(sys.argv[1])
    target = target_level()
    print(f"target graded level (log2 median linear): {target:.2f}")
    os.makedirs("luts2", exist_ok=True)
    report = {}
    for clip, ts in clips.items():
        e, wb, how = params_for(clip, ts, target)
        write_cube(f"luts2/{clip}.cube", e, wb)
        report[clip] = (round(e, 2), [round(x, 3) for x in wb], how)
        print(f"{clip}: exposure {e:+.2f}  wb {np.round(wb, 3)}  ({how})")
    json.dump(report, open("luts2/trims.json", "w"), indent=1)
