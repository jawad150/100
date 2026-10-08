"""anim1_dev.py: critique helpers for anim1 (not used by the render).

    python3 anim1_dev.py strip OUT.png t1 t2 ...    -> side-by-side strip of existing stills (stills/anim1_<t>.png),
                                                     each scaled to 400 px wide, labelled
    python3 anim1_dev.py crop OUT.png t x0 y0 x1 y1  -> 1:1 crop of a still
"""
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import core as K  # noqa: E402

SD = os.path.join(K.OUT, 'anim1', 'stills')


def _load(t):
    p = os.path.join(SD, 'anim1_%06.2f.png' % float(t))
    return cv2.imread(p)


def strip(out, times, w=400):
    ims = []
    for t in times:
        im = _load(t)
        if im is None:
            continue
        h = int(im.shape[0] * w / im.shape[1])
        im = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)
        cv2.putText(im, 't=%s' % t, (8, 26), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(im, 't=%s' % t, (8, 26), cv2.FONT_HERSHEY_DUPLEX, 0.7, (80, 230, 255), 1, cv2.LINE_AA)
        ims.append(im)
    cv2.imwrite(out, np.hstack(ims))


def crop(out, t, x0, y0, x1, y1):
    im = _load(t)
    cv2.imwrite(out, im[int(y0):int(y1), int(x0):int(x1)])


if __name__ == '__main__':
    if sys.argv[1] == 'strip':
        strip(sys.argv[2], sys.argv[3:])
    elif sys.argv[1] == 'crop':
        crop(sys.argv[2], *sys.argv[3:8])
