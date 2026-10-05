"""Fit the smooth parametric grade (grade.py) to each reference clip.

The client's colorist graded shot by shot, so one global transform cannot match every reference.
Instead: fit grade.py's colorist-style parameters per referenced clip (monotonic, artefact-free),
then use the median OR-shot look for clips without a reference.
Writes look/fit3.json.
"""
import json

import numpy as np
from scipy.optimize import minimize

import grade

P = np.load("look/fit_pairs.npz")
NAMES = [str(n) for n in np.load("look/fit.npz")["names"]]
X, Y, C = P["X"], P["Y"], P["C"]
rng = np.random.default_rng(3)

KEYS = ["exposure", "wb_r", "wb_b", "contrast", "mid", "black", "white", "sat", "blue_teal", "blue_sat",
        "skin_warm", "sh_cb", "sh_cr", "mid_cb", "mid_cr", "hi_cb", "hi_cr"]
X0 = np.array([0.0, 0.0, 0.0, 1.0, 0.36, 0.01, 0.9, 1.0, 0.0, 1.0, 0.0, 0, 0, 0, 0, 0, 0], np.float64)
LO = np.array([-3.0, -1.0, -1.0, 0.5, 0.15, 0.0, 0.6, 0.3, -1.0, 0.3, -0.03, -.035, -.035, -.035, -.035, -.03, -.03])
HI = np.array([3.0, 1.0, 1.0, 3.2, 0.6, 0.08, 1.0, 2.2, 2.5, 2.2, 0.04, .035, .035, .035, .035, .03, .03])
# gentle pull toward neutral: tints, extreme saturation / hue moves need real evidence
REG = np.array([0, 0.002, 0.002, 0.002, 0, 0, 0, 0.01, 0.004, 0.01, 1.0, 2.0, 2.0, 2.0, 2.0, 3.0, 3.0])
REF0 = np.array([0, 0, 0, 1.0, 0.36, 0, 0.9, 1.0, 0.0, 1.0, 0, 0, 0, 0, 0, 0, 0])


def to_params(v):
    v = np.clip(v, LO, HI)
    d = dict(zip(KEYS, v))
    return dict(exposure=d["exposure"], wb=(2 ** d["wb_r"], 1.0, 2 ** d["wb_b"]), contrast=d["contrast"],
                mid=d["mid"], black=d["black"], white=d["white"], sat=d["sat"], blue_teal=d["blue_teal"],
                blue_sat=d["blue_sat"], skin_warm=d["skin_warm"], shadow_tint=(d["sh_cb"], d["sh_cr"]),
                mid_tint=(d["mid_cb"], d["mid_cr"]), high_tint=(d["hi_cb"], d["hi_cr"]))


def fit_clip(ci, n=12000):
    ii = np.where(C == ci)[0]
    ii = rng.choice(ii, min(n, len(ii)), replace=False)
    x, y = X[ii], Y[ii]

    def loss(v):
        pr = grade.grade(x, to_params(v))
        r = np.abs(pr - y)
        data = float(np.mean(np.where(r < 0.08, r, 0.08 + 0.3 * (r - 0.08))))   # robust (misregistered pixels)
        return data + float(np.sum(REG * (np.clip(v, LO, HI) - REF0) ** 2))

    best = None
    for start in (X0, X0 + np.r_[0.6, 0, 0, 0.2, 0, 0, 0, 0.3, 0.3, 0, 0, 0, 0, 0, 0, 0, 0],
                  X0 + np.r_[-0.6, 0, 0, 0.2, 0, 0, 0, 0.3, 0.3, 0, 0, 0, 0, 0, 0, 0, 0]):
        r = minimize(loss, start, method="Powell", options=dict(maxiter=6000, xtol=1e-3, ftol=1e-5))
        if best is None or r.fun < best.fun:
            best = r
    v = np.clip(best.x, LO, HI)
    err = np.abs(grade.grade(x, to_params(v)) - y).mean() * 255
    return v, err


if __name__ == "__main__":
    out = {}
    for ci, name in enumerate(NAMES):
        v, err = fit_clip(ci)
        out[name] = dict(zip(KEYS, [round(float(a), 4) for a in v]))
        out[name]["_err8bit"] = round(float(err), 2)
        print(f"{name}: err {err:.2f}  " + " ".join(f"{k}={a:.2f}" for k, a in zip(KEYS, v)), flush=True)
    json.dump(out, open("look/fit3.json", "w"), indent=1)
