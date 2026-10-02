"""Person matte for the whole video with Robust Video Matting (ONNX, CPU).

Reads $GOLD_WORKDIR/src/cc_1080.mov, writes $GOLD_WORKDIR/matte/%05d.png (8-bit alpha).
The recurrent state is reset at hard cuts so the matte doesn't smear across shots.
"""
import os, subprocess, sys, json
import numpy as np
import cv2
import onnxruntime as ort

S = os.environ.get('GOLD_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'workspace')))
W, H = 1080, 1920
CUTS = json.load(open(S + '/work/cuts.json'))  # frame indices where a new shot starts


def main():
    os.makedirs(S + '/matte', exist_ok=True)
    so = ort.SessionOptions()
    so.intra_op_num_threads = int(os.environ.get('THREADS', '4'))
    sess = ort.InferenceSession(S + '/models/rvm_mobilenetv3_fp32.onnx', so, providers=['CPUExecutionProvider'])
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', S + '/src/cc_1080.mov', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         stdout=subprocess.PIPE)
    rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
    ds = np.array([0.25], np.float32)
    i = 0
    cuts = set(CUTS)
    while True:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        if i in cuts:
            rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
        src = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32).transpose(2, 0, 1)[None] / 255.0
        fgr, pha, *rec = sess.run(None, {'src': src, 'r1i': rec[0], 'r2i': rec[1], 'r3i': rec[2], 'r4i': rec[3],
                                         'downsample_ratio': ds})
        a = (np.clip(pha[0, 0], 0, 1) * 255 + 0.5).astype(np.uint8)
        cv2.imwrite(f'{S}/matte/{i:05d}.png', a)
        if i % 100 == 0:
            print('matte', i, flush=True)
        i += 1
    print('done', i)


if __name__ == '__main__':
    main()
