"""Contact sheets for every clip: keyframe-only decode, timestamps burned in.

usage: python3 catalog.py SRC_DIR OUT_DIR [glob]
Writes OUT_DIR/<clip>.jpg (grid of frames with clip-relative timestamps) and
OUT_DIR/index.tsv (clip, duration, width, height, fps).
"""
import glob, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np

SRC, OUT = sys.argv[1], sys.argv[2]
PAT = sys.argv[3] if len(sys.argv) > 3 else "*.MP4"
os.makedirs(OUT, exist_ok=True)
TW = 240  # thumb width
COLS = 8


def probe(path):
    j = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path]))
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    num, den = map(int, v["r_frame_rate"].split("/"))
    w, h = int(v["width"]), int(v["height"])
    rot = 0
    for sd in v.get("side_data_list", []):
        if "rotation" in sd:
            rot = int(sd["rotation"])
    if abs(rot) % 180 == 90:
        w, h = h, w
    return float(j["format"]["duration"]), w, h, num / den


def keyframes(path, w, h):
    th = int(round(TW * h / w / 2)) * 2
    cmd = ["ffmpeg", "-hide_banner", "-v", "info", "-skip_frame", "nokey", "-i", path, "-an",
           "-vf", f"scale={TW}:{th},showinfo", "-fps_mode", "passthrough",
           "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    p = subprocess.run(cmd, capture_output=True)
    times = []
    for line in p.stderr.decode(errors="replace").splitlines():
        if "pts_time:" in line:
            times.append(float(line.split("pts_time:")[1].split()[0]))
    fs = TW * th * 3
    n = len(p.stdout) // fs
    frames = np.frombuffer(p.stdout[:n * fs], np.uint8).reshape(n, th, TW, 3)
    return frames, times[:n], th


def sheet(path):
    name = os.path.basename(path)
    dur, w, h, fps = probe(path)
    frames, times, th = keyframes(path, w, h)
    if not len(frames):
        return name, dur, w, h, fps
    # keep at most 24 frames spread evenly
    idx = np.unique(np.linspace(0, len(frames) - 1, min(24, len(frames))).round().astype(int))
    rows = (len(idx) + COLS - 1) // COLS
    canvas = np.zeros((rows * (th + 2) + 28, COLS * (TW + 2), 3), np.uint8)
    cv2.putText(canvas, f"{name}  {dur:.1f}s  {w}x{h}@{fps:.3f}", (6, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    for k, i in enumerate(idx):
        r, c = divmod(k, COLS)
        y, x = 28 + r * (th + 2), c * (TW + 2)
        canvas[y:y + th, x:x + TW] = frames[i]
        label = f"{times[i]:.1f}"
        cv2.rectangle(canvas, (x, y), (x + 8 + 11 * len(label), y + 20), (0, 0, 0), -1)
        cv2.putText(canvas, label, (x + 4, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 255), 1, cv2.LINE_AA)
    cv2.imwrite(os.path.join(OUT, os.path.splitext(name)[0] + ".jpg"), canvas,
                [cv2.IMWRITE_JPEG_QUALITY, 85])
    return name, dur, w, h, fps


if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(SRC, PAT)))
    with ThreadPoolExecutor(4) as ex:
        rows = list(ex.map(sheet, files))
    with open(os.path.join(OUT, "index.tsv"), "a") as f:
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
            print(*r, sep="\t")
