"""4:3 candidate crops for flash shots: (clip, t, cy, cw, cx) -> labelled tiles (quick neutral grade)."""
import subprocess, sys, json, cv2, numpy as np
cands = json.loads(sys.argv[1]); out = sys.argv[2]
tiles = []
for clip, t, cy, cw, cx in cands:
    p = f"clips/{clip}"
    ch = int(cw * 3 / 4) // 2 * 2; cw2 = int(cw) // 2 * 2
    x = int(min(max(cx - cw2 / 2, 0), 2160 - cw2)); y = int(min(max(cy - ch / 2, 0), 3840 - ch))
    pro = p.endswith(".mov")
    vf = f"crop={cw2}:{ch}:{x}:{y},scale=320:240:in_range={'tv' if pro else 'pc'}:out_range=pc,format=rgb48le,lut3d=file=luts/C9017.cube"
    raw = subprocess.run(["ffmpeg","-v","error","-ss",f"{t}","-i",p,"-frames:v","1","-vf",vf,"-f","rawvideo","-pix_fmt","bgr24","-"],capture_output=True).stdout
    im = np.frombuffer(raw, np.uint8).reshape(240, 320, 3).copy() if len(raw) == 320*240*3 else np.zeros((240,320,3),np.uint8)
    lab = f"{clip[:-4]}@{t} cy{cy} cw{cw}"
    cv2.rectangle(im, (0,0), (8+7*len(lab), 16), (0,0,0), -1); cv2.putText(im, lab, (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,255), 1)
    tiles.append(im)
cols = 5
while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(out, np.vstack([np.hstack(tiles[i:i+cols]) for i in range(0, len(tiles), cols)]), [cv2.IMWRITE_JPEG_QUALITY, 85])
