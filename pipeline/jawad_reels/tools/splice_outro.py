"""splice_outro.py - re-render only a reel's ending and splice it onto the kept full-render intermediate.

    FOSTER_KEEP_PARTS=1 python3 tools/splice_outro.py <slug> --t0 <card start s> --audio <mix A wav> [--workers 3]

1. render.py <slug> --range t0 DUR (lossless yuv444 crf 8 intermediate kept in out/<slug>/parts_range/),
2. frames [0, f0) of out/<slug>/parts_full/video.mp4 + the new range, encoded once with render.py's final settings
   (h264 High CRF 14 preset slow, bt709 tags, AAC 320k) -> out/<slug>/<slug>.mp4 (the master deliver_reel.py takes).
Checks the frame count equals round(DUR * 30).
"""
import argparse
import importlib
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.dirname(HERE)
sys.path.insert(0, PIPE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    ap.add_argument('--t0', type=float, required=True)
    ap.add_argument('--audio', required=True)
    ap.add_argument('--workers', type=int, default=3)
    ap.add_argument('--skip-render', action='store_true')
    a = ap.parse_args()
    os.chdir(PIPE)
    import render as R
    mod = importlib.import_module(a.slug)
    fps = 30
    n = int(round(mod.DUR * fps))
    f0 = int(math.floor(a.t0 * fps + 1e-6))
    out_dir = os.path.abspath(os.path.join(PIPE, '..', '..', 'workspace', 'jawad_reels', 'out', a.slug))
    full = os.path.join(out_dir, 'parts_full', 'video.mp4')
    rng = os.path.join(out_dir, 'parts_range', 'video.mp4')
    if not os.path.exists(full):
        sys.exit('no kept full intermediate: %s' % full)
    if not a.skip_render:
        env = dict(os.environ, FOSTER_KEEP_PARTS='1')
        subprocess.run([sys.executable, 'render.py', a.slug, '--range', '%.6f' % (f0 / fps), '%.6f' % (n / fps + 0.01),
                        '--workers', str(a.workers), '--no-sfx-build', '--no-audio', '--no-share'], check=True, env=env)
    master = os.path.join(out_dir, a.slug + '.mp4')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', full, '-i', rng, '-i', a.audio,
           '-filter_complex', '[0:v]trim=end_frame=%d,setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];'
                              '[a][b]concat=n=2:v=1:a=0,format=yuv420p[v]' % f0,
           '-map', '[v]', '-map', '2:a:0', '-c:v', 'libx264', '-profile:v', 'high', '-preset', 'slow', '-crf', '14',
           '-pix_fmt', 'yuv420p'] + R._vtags() + ['-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-af', 'apad',
                                                  '-t', '%.3f' % (n / fps), '-movflags', '+faststart', master]
    subprocess.run(cmd, check=True)
    pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                                    'stream=nb_read_frames,width,height,r_frame_rate', '-of', 'json', master],
                                   capture_output=True, text=True, check=True).stdout)['streams'][0]
    ok = int(pr['nb_read_frames']) == n
    print('spliced master -> %s  frames %s/%d (outro from f%d)  %s' % (master, pr['nb_read_frames'], n, f0,
                                                                       'OK' if ok else 'FRAME COUNT MISMATCH'))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
