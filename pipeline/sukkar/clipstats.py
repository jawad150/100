import json, os, subprocess, numpy as np
import grade
def frame(path, t, w=360):
    vf = f"scale={w}:-2:in_color_matrix=bt709:in_range=pc:out_range=pc"
    raw = subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",path,"-frames:v","1","-vf",vf,"-f","rawvideo","-pix_fmt","rgb48le","-"],capture_output=True).stdout
    return (np.frombuffer(raw, np.uint16).astype(np.float32)/65535).reshape(-1, w, 3)
clips = {"C8893":[5,25,50],"C8894":[3,15,24],"C8955":[1,5,9],"C8956":[3,12,22],"C8999":[5,20,42],
         "C9017":[4,10,17],"C9019":[3,9,14],"C9028":[1,4,6],"C9031":[4,8,14]}
res = {}
for c, ts in clips.items():
    lins = []
    for t in ts:
        code = frame(f"src/{c}.MP4", t)
        lin = grade.gamut_compress(grade.slog3_to_linear(code) @ grade.M_SG3C_TO_709.T)
        lins.append(lin.reshape(-1, 3))
    lin = np.concatenate(lins)
    Y = lin @ grade.LUMA
    med = float(np.median(Y)); p90 = float(np.percentile(Y, 90))
    # near-neutral pixels: low chroma relative to luma, mid/bright
    rgb = lin / np.maximum(Y[:, None], 1e-6)
    chroma = np.abs(rgb - 1).max(1)
    m = (chroma < 0.25) & (Y > np.percentile(Y, 40))
    neutral = lin[m].mean(0) / lin[m].mean() if m.sum() > 50 else np.ones(3)
    res[c] = dict(median=med, p90=p90, neutral=[round(float(x), 3) for x in neutral], n=int(m.sum()))
    print(f"{c}: median lin {med:.3f} ({np.log2(med/0.18):+.2f} st vs 18%)  p90 {p90:.3f}  neutral rgb {res[c]['neutral']} ({m.sum()} px)")
os.makedirs("look", exist_ok=True)
json.dump(res, open("look/clipstats.json", "w"), indent=1)
