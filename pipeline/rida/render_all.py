"""Renders the Rida reel in parallel chunks, mixes the audio and muxes the final MP4."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
WORK = os.environ.get('REEL_WORKDIR', os.path.join(ROOT, 'workspace', 'rida'))
OUT = os.path.join(WORK, 'out')
JOBS = int(os.environ.get('JOBS', os.cpu_count() or 4))


def main(final_name='rida_japan_yen_reel.mp4'):
    os.makedirs(OUT, exist_ok=True)
    edit = os.path.join(HERE, 'edit.py')
    n = int(subprocess.run([sys.executable, edit, 'nframes'], capture_output=True, text=True, check=True).stdout)
    step = (n + JOBS - 1) // JOBS
    procs, parts = [], []
    for k in range(JOBS):
        a, b = k * step, min(n, (k + 1) * step)
        part = f'{OUT}/part_{k:02d}.mp4'
        parts.append(part)
        procs.append(subprocess.Popen([sys.executable, edit, 'chunk', str(a), str(b), part]))
    for p in procs:
        assert p.wait() == 0
    with open(f'{OUT}/parts.txt', 'w') as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/parts.txt', '-c', 'copy',
                    f'{OUT}/video.mp4'], check=True)
    subprocess.run([sys.executable, edit, 'sfx', f'{OUT}/cues.json'], check=True)
    subprocess.run([sys.executable, os.path.join(HERE, 'audio.py'), f'{WORK}/src/main.mp4', f'{OUT}/cues.json',
                    f'{WORK}/sfx', f'{OUT}/mix.wav', str(n / 30)], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}/video.mp4', '-i', f'{OUT}/mix.wav', '-map', '0:v',
                    '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-profile:v', 'high',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '256k', '-shortest',
                    f'{OUT}/{final_name}'], check=True)
    print('done', f'{OUT}/{final_name}')


if __name__ == '__main__':
    main(*sys.argv[1:])
