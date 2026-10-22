"""Render "No Law Degree? (IC London)": parallel frame chunks -> soundtrack -> master + share encodes.

Usage: python3 render_ff.py [noframes]
"""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(HERE, '..', 'workspace_ic')))
JOBS = int(os.environ.get('JOBS', '4'))
NF = 900   # 30 s at 30 fps


def run(a, b):
    subprocess.run([sys.executable, f'{HERE}/reel_ic.py', 'range', str(a), str(b)], check=True,
                   stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    os.makedirs(f'{S}/out', exist_ok=True)
    if 'noframes' not in sys.argv:
        step = (NF + JOBS * 3 - 1) // (JOBS * 3)
        with ThreadPoolExecutor(JOBS) as ex:
            list(ex.map(lambda c: run(*c), [(a, min(NF, a + step)) for a in range(0, NF, step)]))
    subprocess.run([sys.executable, f'{HERE}/audio_ic.py'], check=True)
    out = f'{S}/out/ic_london_no_law_degree.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', '30', '-i', f'{S}/frames_out/%04d.png',
                    '-i', f'{S}/audio/mix_raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                    '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', out],
                   check=True)
    share = out.replace('.mp4', '_share.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', out, '-c:v', 'libx264', '-preset', 'slow', '-b:v', '7M',
                    '-maxrate', '8.5M', '-bufsize', '12M', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                    '-c:a', 'copy', share], check=True)
    print('wrote', out, share, flush=True)
