"""Shared constants for the P.S. Med Spa reel."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.environ.get('MEDSPA_WORKDIR', os.path.abspath(os.path.join(HERE, '..', '..', 'workspace', 'medspa')))
os.environ.setdefault('REEL_WORKDIR', WS)  # engine.py loads fonts from $REEL_WORKDIR/fonts

FPS = 24000 / 1001
NFRAMES = 971
FW, FH = 1440, 2560          # extracted frame size
W, H = 1080, 1920            # output size

# first frame of each shot in the source edit (ffmpeg scdet), plus the end
CUTS = [0, 78, 137, 196, 246, 310, 362, 498, 570, 637, 770, 837, 884, 937, NFRAMES]
SHOTS = list(zip(CUTS[:-1], CUTS[1:]))

RED = '#EA1D25'       # brand red
CHARCOAL = '#333740'  # brand charcoal


def shot_of(fi):
    for k, (a, b) in enumerate(SHOTS):
        if a <= fi < b:
            return k
    return len(SHOTS) - 1


def frame_path(fi):
    return f'{WS}/frames/{fi:04d}.png'


def matte_path(fi):
    return f'{WS}/matte/{fi:04d}.png'
