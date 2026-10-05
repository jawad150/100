"""Contact sheets of a new clips folder: 8 tiles per clip (rotation-aware), to pick shots quickly."""
import glob, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import cv2, numpy as np
files = sorted(glob.glob("srcB/**/*.MP4", recursive=True) + glob.glob("srcB/**/*.mov", recursive=True))
TW, TH, K = 150, 267, 8
def info(p):
    j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", p]))
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    d = float(j["format"]["duration"])
    head = open(p, "rb").read(3_000_000) if p.lower().endswith(".mp4") else b""
    tail = b""
    if p.lower().endswith(".mp4"):
        with open(p, "rb") as f:
            f.seek(max(0, os.path.getsize(p) - 3_000_000)); tail = f.read()
    gamma = "?"
    for blob in (head, tail):
        i = blob.find(b'CaptureGammaEquation" value="')
        if i >= 0:
            gamma = blob[i + 29: blob.find(b'"', i + 29)].decode()
    return d, v["codec_name"], v.get("pix_fmt"), gamma
def row(p):
    d, codec, pix, gamma = info(p)
    ts = np.linspace(0.3, max(0.3, d - 0.3), K)
    tiles = []
    for t in ts:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", p, "-frames:v", "1", "-vf", f"scale={TW}:{TH}",
                              "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
        im = np.frombuffer(raw, np.uint8).reshape(TH, TW, 3).copy() if len(raw) == TW * TH * 3 else np.zeros((TH, TW, 3), np.uint8)
        cv2.putText(im, f"{t:.1f}", (3, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)
        tiles.append(im)
    strip = np.hstack(tiles)
    lab = np.zeros((22, strip.shape[1], 3), np.uint8)
    name = p.replace("srcB/", "")
    cv2.putText(lab, f"{name}  {d:.1f}s  {codec} {pix} {gamma}", (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    return name, d, codec, gamma, np.vstack([lab, strip])
with ThreadPoolExecutor(4) as ex:
    rows = list(ex.map(row, files))
os.makedirs("new/sheetsB", exist_ok=True)
for i in range(0, len(rows), 6):
    page = np.vstack([r[4] for r in rows[i:i + 6]])
    cv2.imwrite(f"new/sheetsB/page_{i // 6:02d}.jpg", page, [cv2.IMWRITE_JPEG_QUALITY, 80])
for r in rows:
    print(f"{r[0]:28s} {r[1]:6.1f}s {r[2]:6s} {r[3]}")
