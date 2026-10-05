"""Fit the colorist's look: S-Log3 source -> graded reference, from frame-matched pairs.

Model:  out = G( base(code; exposure_c, wb_c) )
  base  = technical S-Log3/S-Gamut3.Cine -> Rec.709 transform + neutral filmic tone curve
  G     = smooth 17^3 3D LUT shared by all clips (the "look")
  exposure_c, wb_c = per-clip trims (what a colorist sets shot by shot)
G is fitted by regularised least squares (trilinear weights + Laplacian smoothness);
trims by grid search; alternated a few times.
Writes look/fit.npz (G, trims) and look/fit_pairs.npz (samples, for QA).
"""
import json
import subprocess

import cv2
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import lsqr

import grade

FPS = 24000 / 1001
W, H = 540, 960
PAIRS = [  # (clip, source file, reference file, ref t0, ref t1, source offset)
    ("C8893", "clips/C8893.MP4", "srcA/mainhero_c8893_ref.mov", 0.3, 8.2, 25.737),
    ("C9021", "clips/C9021.MP4", "srcA/Color Grade Match.mp4", 0.15, 2.2, 17.46),
    ("C8999", "clips/C8999.MP4", "srcA/Color Grade Match.mp4", 2.5, 4.2, 20.40),
    ("C8939", "clips/C8939.MP4", "srcA/Color Grade Match.mp4", 5.95, 7.1, 0.59),
    ("C9019", "clips/C9019.MP4", "srcA/Color Grade Match.mp4", 7.4, 9.25, 7.45),
    ("C9028", "clips/C9028.MP4", "srcA/Color Grade Match.mp4", 9.55, 12.1, -7.37),
]
NEUTRAL = dict(mid=0.40, contrast=1.0, black=0.0, white=1.0)
LUTN = 17


def frame(path, t, rng):
    vf = f"scale={W}:{H}:in_color_matrix=bt709:in_range={rng}:out_range=pc"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.4f}", "-i", path, "-frames:v", "1", "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "rgb48le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint16).reshape(H, W, 3).astype(np.float32) / 65535


def base(code, exposure=0.0, wb=(1.0, 1.0, 1.0)):
    lin = grade.slog3_to_linear(code) @ grade.M_SG3C_TO_709.T
    lin = grade.gamut_compress(lin)
    lin = lin * np.float32(2 ** exposure) * np.asarray(wb, np.float32)
    p = dict(grade.DEFAULT)
    p.update(NEUTRAL)
    return np.clip(grade.tone(lin, p), 0, 1)


def gray(img):
    g = img @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    g = cv2.GaussianBlur(g, (0, 0), 1.2)
    gx, gy = cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1)
    m = np.hypot(gx, gy)
    return (m - m.mean()) / (m.std() + 1e-6)


def align(src_img, ref_img):
    """Affine warp mapping source -> reference geometry (handles punch-in/reframe)."""
    a, b = gray(src_img), gray(ref_img)
    best = None
    for s in np.arange(1.0, 1.61, 0.05):          # the reference is often punched in
        M = np.array([[s, 0, (1 - s) * W / 2], [0, s, (1 - s) * H / 2]], np.float32)
        aw = cv2.warpAffine(a, M, (W, H))
        (dx, dy), resp = cv2.phaseCorrelate(aw.astype(np.float64), b.astype(np.float64))
        if best is None or resp > best[0]:
            best = (resp, s, dx, dy)
    _, s, dx, dy = best
    Mf = np.array([[s, 0, (1 - s) * W / 2 + dx], [0, s, (1 - s) * H / 2 + dy]], np.float32)   # src -> ref
    Wi = cv2.invertAffineTransform(Mf).astype(np.float32)                                       # ref -> src
    try:
        crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-5)
        _, Wi = cv2.findTransformECC(b, a, Wi, cv2.MOTION_AFFINE, crit, None, 5)
    except cv2.error:
        pass
    aw = cv2.warpAffine(a, Wi, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
    score = float((aw * b).mean())
    return Wi, score


def collect(n_per_shot=8, ds=4):
    X, Y, C = [], [], []
    for ci, (clip, sp, rp, r0, r1, off) in enumerate(PAIRS):
        rng_ref = "tv"
        for tr in np.linspace(r0, r1, n_per_shot):
            ref = frame(rp, tr, rng_ref)
            code = frame(sp, tr + off, "pc")
            M, score = align(base(code), ref)
            if score < 0.35:
                print(f"  skip {clip} t={tr:.2f} (align {score:.2f})")
                continue
            warped = cv2.warpAffine(code, M, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderValue=(-1, -1, -1))
            valid = (warped[..., 0] >= 0).astype(np.float32)
            # avoid edges and high-detail areas (misregistration), then average down
            g = gray(ref)
            calm = (np.abs(g) < 1.0).astype(np.float32) * cv2.erode(valid, np.ones((9, 9), np.uint8))
            k = ds
            def pool(img):
                return cv2.resize(img, (W // k, H // k), interpolation=cv2.INTER_AREA)
            m = pool(calm)
            xs, ys = pool(np.where(valid[..., None] > 0, warped, 0)), pool(ref)
            sel = m > 0.95
            X.append(xs[sel]); Y.append(ys[sel]); C.append(np.full(sel.sum(), ci))
            print(f"  {clip} t={tr:.2f} align {score:.2f}  samples {sel.sum()}")
    return np.concatenate(X), np.concatenate(Y), np.concatenate(C)


def trilinear_weights(x, n=LUTN):
    """Sparse matrix (len(x) x n^3) of trilinear interpolation weights for points in [0,1]^3."""
    p = np.clip(x, 0, 1) * (n - 1)
    i0 = np.minimum(np.floor(p).astype(int), n - 2)
    f = p - i0
    rows, cols, vals = [], [], []
    idx = np.arange(len(x))
    for dr in (0, 1):
        wr = f[:, 0] if dr else 1 - f[:, 0]
        for dg in (0, 1):
            wg = f[:, 1] if dg else 1 - f[:, 1]
            for db in (0, 1):
                wb = f[:, 2] if db else 1 - f[:, 2]
                c = ((i0[:, 0] + dr) * n + (i0[:, 1] + dg)) * n + (i0[:, 2] + db)
                rows.append(idx); cols.append(c); vals.append(wr * wg * wb)
    return sparse.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(len(x), n ** 3))


def laplacian(n=LUTN):
    rows, cols, vals = [], [], []
    r = 0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                c = (i * n + j) * n + k
                for di, dj, dk in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
                    if 0 < i + di * 0 and False:
                        pass
                    lo = (i - di, j - dj, k - dk)
                    hi = (i + di, j + dj, k + dk)
                    if min(lo) < 0 or max(hi) > n - 1:
                        continue
                    cl = (lo[0] * n + lo[1]) * n + lo[2]
                    ch = (hi[0] * n + hi[1]) * n + hi[2]
                    rows += [r, r, r]; cols += [cl, c, ch]; vals += [1.0, -2.0, 1.0]
                    r += 1
    return sparse.csr_matrix((vals, (rows, cols)), shape=(r, n ** 3))


LAP = laplacian()


def fit_G(B, Y, lam=0.6):
    A = trilinear_weights(B)
    # identity prior keeps unobserved regions sensible
    g = np.linspace(0, 1, LUTN)
    ident = np.stack(np.meshgrid(g, g, g, indexing="ij"), -1).reshape(-1, 3)
    out = np.zeros((LUTN ** 3, 3), np.float32)
    big = sparse.vstack([A, lam * LAP, 0.02 * sparse.identity(LUTN ** 3)]).tocsr()
    for c in range(3):
        rhs = np.concatenate([Y[:, c], np.zeros(LAP.shape[0]), 0.02 * ident[:, c]])
        out[:, c] = lsqr(big, rhs, atol=1e-7, btol=1e-7, iter_lim=3000)[0]
    return out.reshape(LUTN, LUTN, LUTN, 3)


def apply_G(G, x):
    n = G.shape[0]
    p = np.clip(x, 0, 1) * (n - 1)
    i0 = np.minimum(np.floor(p).astype(int), n - 2)
    f = p - i0
    out = np.zeros_like(x)
    for dr in (0, 1):
        wr = f[..., 0:1] if dr else 1 - f[..., 0:1]
        for dg in (0, 1):
            wg = f[..., 1:2] if dg else 1 - f[..., 1:2]
            for db in (0, 1):
                wb = f[..., 2:3] if db else 1 - f[..., 2:3]
                out += wr * wg * wb * G[i0[..., 0] + dr, i0[..., 1] + dg, i0[..., 2] + db]
    return out


if __name__ == "__main__":
    print("collecting pairs ...")
    X, Y, C = collect()
    np.savez("look/fit_pairs.npz", X=X, Y=Y, C=C)
    nclip = len(PAIRS)
    trims = np.zeros((nclip, 3), np.float32)      # exposure, r gain (log2), b gain (log2)
    for it in range(4):
        B = np.concatenate([base(X[C == ci][None], trims[ci, 0], (2 ** trims[ci, 1], 1.0, 2 ** trims[ci, 2]))[0]
                            for ci in range(nclip)])
        Yo = np.concatenate([Y[C == ci] for ci in range(nclip)])
        G = fit_G(B, Yo)
        err = np.abs(apply_G(G, B[None])[0] - Yo).mean() * 255
        print(f"iter {it}: mean abs error {err:.2f} (8-bit)  trims " + json.dumps(
            {PAIRS[ci][0]: [round(float(v), 2) for v in trims[ci]] for ci in range(nclip)}))
        if it == 3:
            break
        for ci in range(nclip):
            xs, ys = X[C == ci], Y[C == ci]
            if len(xs) > 20000:
                sel = np.random.default_rng(0).choice(len(xs), 20000, replace=False)
                xs, ys = xs[sel], ys[sel]
            best = (1e9, trims[ci].copy())
            for e in np.arange(-1.2, 1.21, 0.1):
                for rg in np.arange(-0.2, 0.21, 0.05):
                    for bg in np.arange(-0.2, 0.21, 0.05):
                        pr = apply_G(G, base(xs[None], e, (2 ** rg, 1.0, 2 ** bg)))[0]
                        er = np.abs(pr - ys).mean()
                        if er < best[0]:
                            best = (er, np.array([e, rg, bg], np.float32))
            trims[ci] = best[1]
        trims -= trims.mean(axis=0, keepdims=True)   # anchor: the look carries the average
    np.savez("look/fit.npz", G=G, trims=trims, names=np.array([p[0] for p in PAIRS]))
    for ci in range(nclip):
        xs, ys = X[C == ci], Y[C == ci]
        pr = apply_G(G, base(xs[None], trims[ci, 0], (2 ** trims[ci, 1], 1.0, 2 ** trims[ci, 2])))[0]
        print(f"{PAIRS[ci][0]}: per-clip error {np.abs(pr - ys).mean() * 255:.2f}  (n={len(xs)})")
