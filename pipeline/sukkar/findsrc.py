"""Find where a graded reference shot comes from in a log source clip (structure match, grade-agnostic)."""
import subprocess, sys, numpy as np, cv2
FPS = 24000 / 1001
def gray_frames(path, t0, dur, w=72, h=128, vf_pre="", fps=None):
    vf = (vf_pre + "," if vf_pre else "") + f"scale={w}:{h}" + (f",fps={fps}" if fps else "")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", path, "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
def feat(f):
    # gradient-magnitude structure, normalised: robust to grade (contrast/colour) differences
    g = np.hypot(cv2.Sobel(f, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(f, cv2.CV_32F, 0, 1, ksize=3))
    g = (g - g.mean()) / (g.std() + 1e-6)
    return g.ravel()
ref_path, ref_t, src_path = sys.argv[1], float(sys.argv[2]), sys.argv[3]
lo, hi = (float(sys.argv[4]), float(sys.argv[5])) if len(sys.argv) > 5 else (0.0, 600.0)
ref = feat(gray_frames(ref_path, ref_t, 0.05)[0])
src = gray_frames(src_path, lo, hi - lo)
scores = np.array([float(np.dot(feat(f), ref) / len(ref)) for f in src])
k = int(np.argmax(scores))
print(f"best match {lo + k / FPS:.3f}s (score {scores[k]:.3f}; 2nd best {np.sort(scores)[-2]:.3f})")
