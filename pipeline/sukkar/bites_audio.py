import json, subprocess, sys, numpy as np
import audio as au
SR = au.SR
def piece(path, t0, t1, pad=0.03):
    # read with padding so splices can crossfade
    return au.read(path, t0 - pad, (t1 - t0) + 2 * pad)
def assemble(pieces, xf=0.022, fin=0.012, fout=0.035):
    pad = 0.03; out = None
    for k, (path, t0, t1) in enumerate(pieces):
        a = piece(path, t0, t1, pad)
        n_pad = int(pad * SR); nx = int(xf * SR)
        # trim padding: keep half the crossfade length on each side of the cut point
        a = a[n_pad - nx // 2: len(a) - n_pad + nx // 2]
        if out is None:
            a = a[nx // 2:]
            out = au.fade(a.copy(), fin, 0)
        else:
            r = np.linspace(0, 1, nx, dtype=np.float32)[:, None]
            gin, gout = np.sin(r * np.pi / 2), np.cos(r * np.pi / 2)
            head = out[:-nx]; tail = out[-nx:] * gout + a[:nx] * gin
            out = np.vstack([head, tail, a[nx:]])
    out = out[:len(out) - nx // 2]
    return au.fade(out, 0, fout)
if __name__ == "__main__":
    bites = json.load(open("tx/bites.json"))
    import wave
    for k, pieces in bites.items():
        a = assemble([tuple(p) for p in pieces])
        x = np.clip(a, -1, 1)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", f"tx/{k}.wav"], input=x.astype(np.float32).tobytes(), check=True)
        print(k, f"{len(a)/SR:.2f}s")
