"""Per-clip grade trims (exposure in stops, partial white balance) on top of the shared look."""
import json
import numpy as np
LOOK = dict(mid=0.30, contrast=1.18, white=0.82, black=0.008, sat=0.84, blue_teal=0.75, blue_sat=0.60,
            skin_warm=0.014, shadow_tint=(0.007, -0.008), mid_tint=(-0.011, 0.004), high_tint=(-0.010, -0.003))
TRIM = {  # exposure stops, wb strength (0..1) toward neutral of measured near-neutrals, manual wb override
    "C8893": (-0.85, 0.5, None), "C8894": (-0.55, 0.5, None), "C8955": (-0.95, 0.8, None),
    "C8956": (0.10, 0.5, None), "C8999": (-1.35, 0.85, None), "C9017": (0.15, 0.45, None),
    "C9019": (-0.10, 0.4, None), "C9028": (0.55, 0.0, (0.90, 1.0, 1.12)), "C9031": (0.55, 0.7, None),
}
STATS = json.load(open("look/clipstats.json"))
# facility reveal opens up: brighter, cleaner whites
OVER = {"C8955": dict(white=0.92, mid=0.35, contrast=1.24), "C8956": dict(white=0.90, mid=0.34),
        "C9031": dict(white=0.86, mid=0.32)}
def params(clip, **over):
    exp, k, manual = TRIM[clip]
    if manual:
        wb = manual
    else:
        n = np.array(STATS[clip]["neutral"])
        g = (1 / n) / (1 / n)[1]
        wb = tuple(float(x) for x in (1 + k * (g - 1)))
    p = dict(LOOK); p.update(exposure=exp, wb=wb); p.update(OVER.get(clip, {})); p.update(over)
    return p
