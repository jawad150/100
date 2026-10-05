"""Full vertical frames (9:16) of every B-roll shot in the v3 edit, graded, labelled: to choose 9:16 framings."""
import subprocess, sys
import cv2, numpy as np
sys.argv = [sys.argv[0]]
sys.path.insert(0, ".")
import reel_sukkar as R

TW, TH = 216, 384
tiles = []
prev = 0.0
for end_s, spec, trans in R.TL:
    if spec.get("kind") != "broll":
        prev = end_s
        continue
    d = end_s - prev
    for frac in (0.1, 0.9) if d > 1.2 else (0.5,):
        t = spec["t"] + (-frac * d if spec.get("reverse") else frac * d)
        vf = (f"scale={TW*2}:{TH*2}:flags=lanczos:in_color_matrix=bt709:in_range={spec['rng']}:out_range=pc,"
              f"format=rgb48le,lut3d=file={spec['lut']}:interp=tetrahedral,scale={TW}:{TH},format=bgr24")
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0, t):.3f}", "-i", spec["src"], "-frames:v", "1",
                              "-vf", vf, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
        im = np.frombuffer(raw, np.uint8).reshape(TH, TW, 3).copy() if len(raw) == TW * TH * 3 else np.zeros((TH, TW, 3), np.uint8)
        # mark the old 4:3 crop window
        cx, cy, cw = spec["crop"]
        ch = cw * 3 / 4
        s = TW / 2160
        x0, y0 = int((cx - cw / 2) * s), int((cy - ch / 2) * s)
        cv2.rectangle(im, (x0, y0), (int(x0 + cw * s), int(y0 + ch * s)), (0, 255, 255), 1)
        lab = f"{prev:.2f} {spec['label']}"
        cv2.putText(im, lab, (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 3)
        cv2.putText(im, lab, (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        # grid lines every 10% of height
        for k in range(1, 10):
            cv2.line(im, (0, int(TH * k / 10)), (6, int(TH * k / 10)), (0, 0, 255), 1)
        tiles.append(im)
    prev = end_s
cols = 10
rows = (len(tiles) + cols - 1) // cols
sheet = np.zeros((rows * TH, cols * TW, 3), np.uint8)
for i, im in enumerate(tiles):
    r, c = divmod(i, cols)
    sheet[r * TH:(r + 1) * TH, c * TW:(c + 1) * TW] = im
half = (rows + 1) // 2
cv2.imwrite("v916/full_a.jpg", sheet[:half * TH], [cv2.IMWRITE_JPEG_QUALITY, 85])
cv2.imwrite("v916/full_b.jpg", sheet[half * TH:], [cv2.IMWRITE_JPEG_QUALITY, 85])
print(len(tiles), "tiles", rows, "rows")
