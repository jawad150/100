"""Person alpha mattes with Robust Video Matting (MobileNetV3, ONNX fp16).

The recurrent state is reset at every cut so each shot is matted on its own.
Usage: python3 pipeline/medspa/matte.py [first_shot last_shot]
"""
import os, sys
import numpy as np, cv2
import onnxruntime as ort
from common import WS, SHOTS, frame_path, matte_path

RATIO = 0.2   # 1440x2560 -> 288x512 internal


def run(shots):
    os.makedirs(f'{WS}/matte', exist_ok=True)
    so = ort.SessionOptions()
    so.intra_op_num_threads = 4
    sess = ort.InferenceSession(f'{WS}/src/rvm_fp16.onnx', so, providers=['CPUExecutionProvider'])
    for k in shots:
        a, b = SHOTS[k]
        rec = [np.zeros([1, 1, 1, 1], np.float16)] * 4
        # two warm-up passes over the first frames so the state settles before frame a
        order = list(range(a, min(a + 6, b))) + list(range(a, b))
        for n, fi in enumerate(order):
            img = cv2.imread(frame_path(fi))[..., ::-1]
            x = (img.astype(np.float32) / 255).transpose(2, 0, 1)[None].astype(np.float16)
            fgr, pha, *rec = sess.run(None, {'src': x, 'r1i': rec[0], 'r2i': rec[1], 'r3i': rec[2], 'r4i': rec[3],
                                             'downsample_ratio': np.array([RATIO], np.float32)})
            if n >= min(6, b - a):
                cv2.imwrite(matte_path(fi), (pha[0, 0].astype(np.float32) * 255).clip(0, 255).astype(np.uint8))
        print('shot', k, a, b, flush=True)


if __name__ == '__main__':
    if len(sys.argv) > 2:
        run(range(int(sys.argv[1]), int(sys.argv[2]) + 1))
    else:
        run(range(len(SHOTS)))
