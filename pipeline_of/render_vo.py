"""Render the voiceover cut in parallel chunks, then encode + mux the -14 LUFS mix."""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(HERE, '..', 'workspace_of')))
FPS, NF = 30, 882
JOBS = int(os.environ.get('JOBS', '4'))


def run(a, b):
    subprocess.run([sys.executable, f'{HERE}/reel_vo.py', 'range', str(a), str(b)], check=True,
                   stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    if 'noframes' not in sys.argv:
        step = (NF + JOBS * 3 - 1) // (JOBS * 3)
        with ThreadPoolExecutor(JOBS) as ex:
            list(ex.map(lambda c: run(*c), [(a, min(NF, a + step)) for a in range(0, NF, step)]))
    subprocess.run([sys.executable, f'{HERE}/audio_vo.py'], check=True)
    out = f'{S}/out/organic_fostering_day_in_the_life_vo.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{S}/frames_vo/%04d.png',
                    '-i', f'{S}/audio/mix_vo_raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                    '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', out],
                   check=True)
    share = out.replace('.mp4', '_share.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', out, '-c:v', 'libx264', '-preset', 'slow', '-b:v', '11M',
                    '-maxrate', '13M', '-bufsize', '22M', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                    '-c:a', 'copy', share], check=True)
    print('wrote', out, share)
