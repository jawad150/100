"""Shared constants for the Clinic for Plastic Surgery (surgery B-roll + testimonial) reel."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.environ.get('SURGERY_WORKDIR', os.path.abspath(os.path.join(HERE, '..', '..', 'workspace', 'surgery')))
os.environ.setdefault('REEL_WORKDIR', WS)  # engine.py loads fonts from $REEL_WORKDIR/fonts

FPS = 24000 / 1001
NFRAMES = 1324               # frames in the source edit
NOUT = 1324                  # output frames
FW, FH = 1440, 2560          # extracted frame size
W, H = 1080, 1920            # output size

# first frame of each shot in the source edit (ffmpeg scdet), plus the end
CUTS = [0, 89, 182, 310, 426, 492, 617, 744, 805, 843, 914, 940, 1031, 1127, 1166, 1203, 1260, NFRAMES]
SHOTS = list(zip(CUTS[:-1], CUTS[1:]))

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
