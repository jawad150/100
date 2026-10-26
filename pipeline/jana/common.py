"""Shared constants for the P.S. Med Spa "Meet Jana" reel."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.environ.get('JANA_WORKDIR', os.path.abspath(os.path.join(HERE, '..', '..', 'workspace', 'jana')))
os.environ.setdefault('REEL_WORKDIR', WS)  # engine.py loads fonts from $REEL_WORKDIR/fonts

FPS = 24000 / 1001
# The delivered edit ('Meet Jana.mov') runs 1665 frames, but its audio is digital silence
# after 42.27 s: the last 27 s are silent B-roll. The reel ends with her last word.
NFRAMES = 1036               # source frames used
NOUT = 1036                  # output frames (fade to black over the last ~0.7 s)
FW, FH = 1440, 2560          # extracted frame size
W, H = 1080, 1920            # output size

# first frame of each shot in the source edit (frame differencing with the laser /
# IPL flashes inside shots 4 and 12 ruled out), plus the end
CUTS = [0, 49, 110, 175, 249, 359, 425, 502, 556, 615, 668, 723, 774, 893, NFRAMES]
SHOTS = list(zip(CUTS[:-1], CUTS[1:]))

RED = '#EA1D25'       # brand red
CHARCOAL = '#333740'  # brand charcoal


def shot_of(fi):
    for k, (a, b) in enumerate(SHOTS):
        if a <= fi < b:
            return k
    return len(SHOTS) - 1


def frame_path(fi):
    return f'{WS}/frames/{fi:04d}.jpg'


def matte_path(fi):
    return f'{WS}/matte/{fi:04d}.png'
