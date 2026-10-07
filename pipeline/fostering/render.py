"""render.py: CLI that renders a reel module (pipeline/fostering/<reel>.py) to stills, contact sheets,
previews and the final parallel-chunked H.264 master.

    python3 render.py reel1 [--stills 1.0,5.5,...] [--sheet N] [--preview] [--range a b]
                            [--workers 4] [--samples k] [--crf 14] [--audio PATH | --no-audio] [--jpg]
                            [--sfx] [--no-sfx-build]
    python3 render.py selftest      # typical-frame benchmark + demo stills -> out/selftest/render_*.png

REEL MODULE CONTRACT (pure functions of t; no state carried between calls, frames render out of order
in several processes):
    DUR = 26.0                  # seconds
    LOOK = 'neon'               # core look for the default finishing stack
    BPM = 120
    def draw(t): -> canvas      # (1920, 1080, 4) linear premultiplied float32 at exact time t (no motion blur)
    def post(canvas, t): -> canvas   # finishing (bloom, grain...); default core.post(canvas, LOOK, t)
    def samples(t): -> int      # optional sub-frame samples per frame (default 3; more on whips)
    def cues(): -> list         # optional SFX cue list, written to out/<reel>/cues.json
    def prewarm(): ...          # optional, called once per worker process before rendering

MODES (outputs in workspace3/out/<reel>/)
    --stills 1.0,5.5   full-quality stills -> stills/<reel>_<t>.png (+ .jpg with --jpg)
    --sheet N          N evenly spaced frames with timestamps -> sheet.jpg
    --preview          1 sample, every 2nd frame at 15 fps, crf 23 -> <reel>_preview.mp4
    --range a b        render only [a, b) seconds -> <reel>_<a>-<b>.mp4
    (default)          full render: contiguous frame chunks across --workers spawn processes, each writing a
                       yuv444 crf 8 intermediate; concatenated and muxed with audio/<reel>_sfx.wav when it
                       exists -> <reel>.mp4 (crf 14, preset slow, +faststart) and <reel>_share.mp4.
    SFX: when the reel has cues(), audio/<reel>_sfx.wav is (re)mixed automatically with audio.build_reel if it
         is missing or older than the reel module (--sfx forces it, --no-sfx-build disables it, --audio PATH
         uses a given wav as is). The mix is SFX only (no music), -18 LUFS, <= -1.5 dBTP.
    Per-frame timing statistics (and the workers' peak memory) are printed and saved to render_stats.json.
    Workers are spawned processes (concurrent.futures): if one dies (e.g. OOM-killed) the unfinished chunks are
    retried with one worker fewer instead of hanging. Worker cache defaults: FOSTER_S3_CACHE_MB=448, and with 3+
    workers FOSTER_TYPE_CACHE_MB=256 (explicit env settings win).

Python API (used by tests / other tools):
    render_still(mod, t, samples=None) -> uint8 (H, W, 3)
    load_reel('reel_demo') -> module
    benchmark_typical(n=6, look='neon') -> seconds per typical single-sample frame on one core
    run_jobs(fn, jobs, workers) -> results in order (robust spawn pool); ensure_sfx(mod, reel, force=False)
"""
import argparse
import gc
import importlib
import json
import math
import multiprocessing as mp
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
for _v in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')        # spawned workers inherit this before numpy loads

_MOD_CACHE = {}


def load_reel(name):
    """Import a reel module by name from pipeline/fostering and check its contract."""
    if name in _MOD_CACHE:
        return _MOD_CACHE[name]
    name = os.path.splitext(os.path.basename(name))[0]
    mod = importlib.import_module(name)
    for attr in ('DUR', 'draw'):
        if not hasattr(mod, attr):
            raise AttributeError('reel module %s lacks %s' % (name, attr))
    _MOD_CACHE[name] = mod
    return mod


def _samples(mod, t, override):
    if override:
        return int(override)
    if hasattr(mod, 'samples'):
        return max(1, int(mod.samples(t)))
    return 3


def render_still(mod, t, samples=None, shutter=0.5):
    """Render one finished frame of a reel module at time t -> uint8 RGB (H, W, 3)."""
    import core as K
    n = _samples(mod, t, samples)
    acc = K.render_frame(mod.draw, t, n, shutter)
    if hasattr(mod, 'post'):
        out = mod.post(acc, t)
        acc = acc if out is None else out
    else:
        acc = K.post(acc, getattr(mod, 'LOOK', 'neon'), t)
    return K.to_srgb8(acc, t)


# ---------------------------------------------------------------------------------------------- workers
_W = {}


def _worker_setup(reel):
    if _W.get('reel') == reel:
        return _W['mod']
    try:
        os.nice(int(os.environ.get('FOSTER_NICE', '0')))
    except (OSError, AttributeError):
        pass
    import core as K  # noqa: F401  (cv2 thread count is read from FOSTER_CV_THREADS at import)
    mod = load_reel(reel)
    if hasattr(mod, 'prewarm'):
        mod.prewarm()
    _W['reel'] = reel
    _W['mod'] = mod
    return mod


def _chunk_job(job):
    """Render a contiguous list of frame indices into one intermediate video."""
    import core as K
    mod = _worker_setup(job['reel'])
    times = []
    wtag = '[%s %d/%d]' % (job['reel'], job['chunk'] + 1, job['nchunks'])
    t_start = time.time()
    with K.FFWriter(job['path'], fps=job['fps_out'], crf=job['crf'], preset=job['preset'],
                    pix_fmt=job['pix_fmt'], faststart=False) as fw:
        for k, fi in enumerate(job['frames']):
            t = fi / K.FPS
            t0 = time.time()
            u8 = render_still(mod, t, job['samples'])
            fw.write(u8)
            if k % 8 == 7:
                gc.collect()            # safety net: frees any per-frame reference cycles in reel code
            dt = time.time() - t0
            times.append((fi, t, dt, _samples(mod, t, job['samples'])))
            if (k + 1) % job['report'] == 0 or k + 1 == len(job['frames']):
                el = time.time() - t_start
                eta = el / (k + 1) * (len(job['frames']) - k - 1)
                print('%s frame %d/%d  t=%.2fs  %.2fs/frame  eta %.0fs' % (
                    wtag, k + 1, len(job['frames']), t, el / (k + 1), eta), flush=True)
    return {'chunk': job['chunk'], 'path': job['path'], 'times': times, 'max_rss_mb': _max_rss_mb()}


def _max_rss_mb():
    try:
        import resource
        return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)
    except Exception:
        return None


def _still_job(job):
    mod = _worker_setup(job['reel'])
    t0 = time.time()
    u8 = render_still(mod, job['t'], job['samples'])
    return job['t'], u8, time.time() - t0


# ---------------------------------------------------------------------------------------------- helpers
def _ff(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-3000:])
        raise RuntimeError('ffmpeg failed: ' + ' '.join(cmd))
    return r


def _worker_env(workers):
    """Per-worker defaults inherited by the spawned processes (explicit env settings win). Every worker holds its
    own caches, so with 3-4 workers they are trimmed to keep the pool inside the ~14 GB memory limit."""
    os.environ.setdefault('FOSTER_CV_THREADS', '1')
    if workers > 1:
        os.environ.setdefault('FOSTER_S3_CACHE_MB', '448')        # sprites3d decoded frames (default 768)
    if workers > 2:
        os.environ.setdefault('FOSTER_TYPE_CACHE_MB', '256')      # type3d sprites (default 400)


def run_jobs(fn, jobs, workers):
    """Run fn(job) for every job in `workers` spawned processes and return the results in job order. Unlike
    multiprocessing.Pool (which waits forever when a worker is OOM-killed), a dead worker raises
    BrokenProcessPool here: the unfinished jobs are retried with one worker fewer (in-process at 1)."""
    from concurrent.futures import ProcessPoolExecutor, as_completed
    from concurrent.futures.process import BrokenProcessPool
    results = {}
    pending = list(range(len(jobs)))
    w = max(1, min(int(workers), len(jobs)))
    while pending:
        if w <= 1:
            for i in pending:
                results[i] = fn(jobs[i])
            break
        _worker_env(w)
        try:
            with ProcessPoolExecutor(max_workers=w, mp_context=mp.get_context('spawn')) as ex:
                futs = {ex.submit(fn, jobs[i]): i for i in pending}
                for f in as_completed(futs):
                    results[futs[f]] = f.result()
            pending = []
        except BrokenProcessPool:
            pending = [i for i in pending if i not in results]
            w -= 1
            print('!! a render worker died (out of memory?) - retrying %d job(s) with %d worker(s)' % (
                len(pending), w), flush=True)
    return [results[i] for i in range(len(jobs))]


def _stats(times, wall, label):
    import numpy as np
    if not times:
        return {}
    dts = np.array([x[2] for x in times])
    order = np.argsort(-dts)[:6]
    st = {
        'label': label, 'frames': len(times), 'wall_s': round(wall, 2),
        'mean_s': round(float(dts.mean()), 3), 'median_s': round(float(np.median(dts)), 3),
        'p90_s': round(float(np.percentile(dts, 90)), 3), 'max_s': round(float(dts.max()), 3),
        'min_s': round(float(dts.min()), 3), 'cpu_s': round(float(dts.sum()), 1),
        'effective_fps': round(len(times) / max(wall, 1e-6), 2),
        'slowest': [{'t': round(times[i][1], 3), 's': round(float(dts[i]), 3), 'samples': times[i][3]}
                    for i in order],
    }
    by_samples = {}
    for x in times:
        by_samples.setdefault(x[3], []).append(x[2])
    st['by_samples'] = {str(k): {'n': len(v), 'mean_s': round(float(np.mean(v)), 3)} for k, v in by_samples.items()}
    print('\n== %s timing: %d frames in %.1fs wall (%.2f fps)  per frame: mean %.2fs  median %.2fs  p90 %.2fs  '
          'max %.2fs' % (label, st['frames'], wall, st['effective_fps'], st['mean_s'], st['median_s'],
                         st['p90_s'], st['max_s']))
    for k, v in sorted(st['by_samples'].items()):
        print('   samples=%s: %d frames, mean %.2fs' % (k, v['n'], v['mean_s']))
    print('   slowest: ' + ', '.join('t=%.2f %.2fs' % (s['t'], s['s']) for s in st['slowest']))
    return st


def _split(frames, nchunks):
    n = len(frames)
    nchunks = max(1, min(nchunks, n))
    out = []
    for c in range(nchunks):
        a = c * n // nchunks
        b = (c + 1) * n // nchunks
        if b > a:
            out.append(frames[a:b])
    return out


def _render_video(reel, frames, out_path, fps_out, crf, preset, pix_fmt, workers, samples, parts_dir, label):
    """Render frames in parallel chunks into intermediates and concatenate them (stream copy)."""
    os.makedirs(parts_dir, exist_ok=True)
    for f in os.listdir(parts_dir):
        if f.startswith('part_'):
            os.remove(os.path.join(parts_dir, f))
    # a few more chunks than workers balances uneven sections; each chunk is still contiguous
    nch = workers * 3 if len(frames) > workers * 24 else workers
    chunks = _split(frames, nch)
    jobs = [{'reel': reel, 'frames': ch, 'chunk': i, 'nchunks': len(chunks),
             'path': os.path.join(parts_dir, 'part_%03d.mp4' % i), 'fps_out': fps_out, 'crf': crf,
             'preset': preset, 'pix_fmt': pix_fmt, 'samples': samples,
             'report': max(1, min(15, len(ch) // 4 or 1))} for i, ch in enumerate(chunks)]
    t0 = time.time()
    results = run_jobs(_chunk_job, jobs, workers)
    wall = time.time() - t0
    results.sort(key=lambda r: r['chunk'])
    lst = os.path.join(parts_dir, 'list.txt')
    with open(lst, 'w') as f:
        for r in results:
            f.write("file '%s'\n" % os.path.abspath(r['path']))
    _ff(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out_path])
    times = [x for r in results for x in r['times']]
    st = _stats(times, wall, label)
    rss = [r.get('max_rss_mb') for r in results if r.get('max_rss_mb')]
    if rss:
        st['worker_max_rss_mb'] = max(rss)
        print('   worker peak memory: %d MB' % max(rss))
    return st


def _vtags():
    return ['-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv']


def _final_encode(src, audio, out_path, crf=14, preset='slow', t_offset=0.0, dur=None):
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', src]
    if audio:
        if t_offset > 0:
            cmd += ['-ss', '%.3f' % t_offset]
        cmd += ['-i', audio]
    cmd += ['-map', '0:v:0']
    if audio:
        cmd += ['-map', '1:a:0']
    cmd += ['-vf', 'format=yuv420p', '-c:v', 'libx264', '-profile:v', 'high', '-preset', preset, '-crf', str(crf),
            '-pix_fmt', 'yuv420p'] + _vtags()
    if audio:
        cmd += ['-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-af', 'apad']
        if dur:
            cmd += ['-t', '%.3f' % dur]
        else:
            cmd += ['-shortest']
    cmd += ['-movflags', '+faststart', out_path]
    _ff(cmd)


def _share_encode(src, out_path):
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-c:v', 'libx264', '-profile:v', 'high',
           '-preset', 'medium', '-crf', '21', '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p'] + _vtags()
    cmd += ['-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', out_path]
    _ff(cmd)


def _probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                        'stream=codec_name,profile,width,height,pix_fmt,r_frame_rate,color_space,color_primaries,'
                        'color_transfer,sample_rate,nb_frames:format=duration,size', '-of', 'json', path],
                       stdout=subprocess.PIPE, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {}


def _write_cues(mod, outdir):
    if not hasattr(mod, 'cues'):
        return None
    try:
        cues = mod.cues()
    except Exception as e:  # cue lists are optional; never block a render on them
        print('cues() failed:', e)
        return None
    p = os.path.join(outdir, 'cues.json')
    with open(p, 'w') as f:
        json.dump({'reel': mod.__name__, 'dur': mod.DUR, 'bpm': getattr(mod, 'BPM', None), 'cues': cues}, f,
                  indent=1, default=float)
    print('wrote', p, '(%d cues)' % len(cues))
    return p


# ---------------------------------------------------------------------------------------------- modes
def do_stills(reel, times, samples, workers, outdir, jpg=False):
    import cv2
    sd = os.path.join(outdir, 'stills')
    os.makedirs(sd, exist_ok=True)
    jobs = [{'reel': reel, 't': t, 'samples': samples} for t in times]
    res = run_jobs(_still_job, jobs, workers)
    paths = []
    for t, u8, dt in res:
        p = os.path.join(sd, '%s_%06.2f.png' % (reel, t))
        cv2.imwrite(p, cv2.cvtColor(u8, cv2.COLOR_RGB2BGR))
        paths.append(p)
        if jpg:
            cv2.imwrite(p[:-4] + '.jpg', cv2.cvtColor(u8, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 94])
        print('still t=%.2f  %.2fs  -> %s' % (t, dt, p))
    return paths


def do_sheet(reel, n, samples, workers, outdir, dur, bpm=None):
    import cv2
    import numpy as np
    times = [(k + 0.5) * dur / n for k in range(n)]
    jobs = [{'reel': reel, 't': t, 'samples': samples} for t in times]
    t0 = time.time()
    res = run_jobs(_still_job, jobs, workers)
    cols = int(math.ceil(math.sqrt(n * 1.6)))
    cols = min(cols, n)
    rows = int(math.ceil(n / cols))
    tw, th = 270, 480
    sheet = np.full((rows * (th + 6) + 6, cols * (tw + 6) + 6, 3), 18, np.uint8)
    for k, (t, u8, dt) in enumerate(res):
        th_img = cv2.resize(u8, (tw, th), interpolation=cv2.INTER_AREA)
        lab = 't=%.2fs' % t + ('  b%.1f' % (t * bpm / 60.0) if bpm else '')
        cv2.putText(th_img, lab, (8, 24), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(th_img, lab, (8, 24), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 235, 120), 1, cv2.LINE_AA)
        r, c = divmod(k, cols)
        y, x = 6 + r * (th + 6), 6 + c * (tw + 6)
        sheet[y:y + th, x:x + tw] = th_img
    p = os.path.join(outdir, 'sheet.jpg')
    cv2.imwrite(p, cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
    dts = [r[2] for r in res]
    print('sheet: %d frames in %.1fs (mean %.2fs/frame) -> %s' % (n, time.time() - t0, sum(dts) / len(dts), p))
    return p


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('reel')
    ap.add_argument('--stills', type=str, default=None)
    ap.add_argument('--sheet', type=int, default=None)
    ap.add_argument('--preview', action='store_true')
    ap.add_argument('--range', type=float, nargs=2, default=None)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--samples', type=int, default=None)
    ap.add_argument('--crf', type=int, default=14)
    ap.add_argument('--audio', type=str, default=None)
    ap.add_argument('--no-audio', action='store_true')
    ap.add_argument('--jpg', action='store_true')
    ap.add_argument('--no-share', action='store_true')
    ap.add_argument('--sfx', action='store_true', help='rebuild audio/<reel>_sfx.wav from cues() first')
    ap.add_argument('--no-sfx-build', action='store_true', help='never (re)build the SFX mix automatically')
    a = ap.parse_args(argv)

    os.environ.setdefault('FOSTER_CV_THREADS', '1' if a.workers > 1 else '2')
    import core as K
    reel = os.path.splitext(os.path.basename(a.reel))[0]
    mod = load_reel(reel)
    outdir = os.path.join(K.OUT, reel)
    os.makedirs(outdir, exist_ok=True)
    dur = float(mod.DUR)
    bpm = getattr(mod, 'BPM', None)
    audio = None
    if not a.no_audio:
        audio = a.audio or os.path.join(K.AUDIO, '%s_sfx.wav' % reel)
        if not a.audio and not a.no_sfx_build:
            audio = ensure_sfx(mod, reel, force=a.sfx) or audio
        if not os.path.exists(audio):
            audio = None
    did = False
    if a.stills:
        did = True
        times = [float(x) for x in a.stills.split(',') if x.strip()]
        do_stills(reel, times, a.samples, a.workers, outdir, a.jpg)
    if a.sheet:
        did = True
        do_sheet(reel, a.sheet, a.samples, a.workers, outdir, dur, bpm)
    if a.preview:
        did = True
        n = int(round(dur * K.FPS))
        frames = list(range(0, n, 2))
        out = os.path.join(outdir, '%s_preview.mp4' % reel)
        tmp = os.path.join(outdir, 'parts_preview', 'video.mp4')
        st = _render_video(reel, frames, tmp, K.FPS / 2, 23, 'veryfast', 'yuv420p', a.workers, a.samples or 1,
                           os.path.join(outdir, 'parts_preview'), 'preview')
        if audio:
            _ff(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-i', audio, '-map', '0:v:0', '-map', '1:a:0',
                 '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart',
                 out])
        else:
            _ff(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-c', 'copy', '-movflags', '+faststart', out])
        print('preview ->', out)
        _save_stats(outdir, 'preview', st)
    if a.range or not did:
        _write_cues(mod, outdir)
        n = int(round(dur * K.FPS))
        if a.range:
            f0 = max(0, int(math.floor(a.range[0] * K.FPS + 1e-6)))
            f1 = min(n, int(math.ceil(a.range[1] * K.FPS - 1e-6)))
            frames = list(range(f0, f1))
            name = '%s_%.2f-%.2f' % (reel, a.range[0], a.range[1])
        else:
            frames = list(range(n))
            name = reel
        parts = os.path.join(outdir, 'parts_' + ('range' if a.range else 'full'))
        inter = os.path.join(parts, 'video.mp4')
        st = _render_video(reel, frames, inter, K.FPS, 8, 'fast', 'yuv444p', a.workers, a.samples, parts,
                           'range' if a.range else 'full')
        out = os.path.join(outdir, name + '.mp4')
        t0 = time.time()
        _final_encode(inter, audio, out, crf=a.crf, preset='slow', t_offset=frames[0] / K.FPS if frames else 0,
                      dur=len(frames) / K.FPS)
        print('master -> %s (%.1fs encode)%s' % (out, time.time() - t0, '  + audio ' + audio if audio else
                                                 '  (no SFX wav found: video only)'))
        if not a.range and not a.no_share:
            sp = os.path.join(outdir, name + '_share.mp4')
            _share_encode(out, sp)
            print('share  ->', sp)
        pr = _probe(out)
        st['probe'] = pr
        _save_stats(outdir, 'range' if a.range else 'full', st)
        for s in pr.get('streams', []):
            print('   stream:', {k: s.get(k) for k in ('codec_name', 'profile', 'width', 'height', 'pix_fmt',
                                                       'r_frame_rate', 'color_space', 'sample_rate', 'nb_frames')})
        if not os.environ.get('FOSTER_KEEP_PARTS'):
            shutil.rmtree(parts, ignore_errors=True)


def ensure_sfx(mod, reel, force=False):
    """Mix workspace3/audio/<reel>_sfx.wav (+ _stem.wav) from the reel's cues() with audio.build_reel when it
    is missing, older than the reel module (cues changed) or force=True. Returns the wav path or None."""
    import core as K
    if not hasattr(mod, 'cues'):
        return None
    wav = os.path.join(K.AUDIO, '%s_sfx.wav' % reel)
    src = getattr(mod, '__file__', None)
    existed = os.path.exists(wav)
    stale = (not existed) or bool(src and os.path.getmtime(src) > os.path.getmtime(wav))
    if not (force or stale):
        return wav
    import audio as A
    os.makedirs(K.AUDIO, exist_ok=True)
    t0 = time.time()
    rep = A.build_reel(reel, verbose=False)
    print('SFX mix (%s) -> %s  %.2f LUFS  %.2f dBTP  (%.1fs)' % (
        'forced' if force else ('missing' if not existed else 'cues changed'), wav,
        rep['integrated_lufs'], rep['true_peak_dbtp'], time.time() - t0))
    for p in rep.get('placed', []):
        if p.get('warn'):
            print('   cue warning: %s at %.2fs: %s' % (p.get('name'), p.get('t', 0.0), p['warn']))
    return wav


def _save_stats(outdir, label, st):
    p = os.path.join(outdir, 'render_stats.json')
    allst = {}
    if os.path.exists(p):
        try:
            with open(p) as f:
                allst = json.load(f)
        except (OSError, json.JSONDecodeError):
            allst = {}
    allst[label] = st
    with open(p, 'w') as f:
        json.dump(allst, f, indent=1)


def benchmark_typical(n=6, look='neon'):
    """Time the brief's 'typical frame' on one core: animated background with a moving camera, one graded
    footage plane (DOF), 6 glow sprites, 170 dust particles, post and sRGB conversion. Returns seconds."""
    import numpy as np
    import core as K
    import footage as F
    clip = F.Clip('c12')
    dust = K.Particles(170, seed=3)
    cards = []
    for i in range(6):
        a = K.rrect_alpha(300, 110, 55, 16)
        spr = np.dstack([np.ones(a.shape + (3,), np.float32) * 0.08 * a[..., None], a * 0.5]).astype(np.float32)
        cards.append(K.glow(spr, K.C['HOT_PINK'], (6, 20), 0.4))

    def frame(t):
        cam = K.Cam(pos=(20 * t, 0, -1500 + 60 * t), yaw=4 - 2 * t, aperture=40)
        cv = K.background(look, t, cam)
        foot = clip.get(6.0 + t, 760, 1060, zoom=1.08, look=look)
        K.draw_plane(cv, foot, cam, (0, -40, 150), 780, rot=(4, -14 + 3 * t, -2))
        for i, s in enumerate(cards):
            K.draw_billboard(cv, s, cam, (-380 + 150 * i, -700 + 290 * i, -300 + 260 * i), 320)
        dust.draw(cv, cam, t)
        K.post(cv, look, t)
        return K.to_srgb8(cv, t)
    frame(0.0)
    frame(0.05)
    t0 = time.time()
    for k in range(n):
        frame(0.1 + k / 30.0)
    return (time.time() - t0) / n


def selftest():
    """python3 render.py selftest: typical-frame benchmark, demo stills + a mini contact sheet."""
    import cv2
    import numpy as np
    import core as K
    os.makedirs(K.SELFTEST, exist_ok=True)
    os.environ['FOSTER_CV_THREADS'] = '1'
    import cv2 as _cv
    _cv.setNumThreads(1)
    dt = benchmark_typical()
    print('typical frame, 1 sample, 1 core: %.3f s' % dt)
    mod = load_reel('reel_demo')
    if hasattr(mod, 'prewarm'):
        mod.prewarm()
    tiles = []
    for t in (0.35, 1.0, 2.6):
        u8 = render_still(mod, t)
        tiles.append(cv2.resize(u8, (540, 960), interpolation=cv2.INTER_AREA))
    p = os.path.join(K.SELFTEST, 'render_demo_stills.png')
    cv2.imwrite(p, cv2.cvtColor(np.concatenate(tiles, 1), cv2.COLOR_RGB2BGR))
    print('wrote', p)
    with open(os.path.join(K.SELFTEST, 'render_benchmark.json'), 'w') as f:
        json.dump({'typical_frame_1sample_1core_s': round(dt, 3)}, f)
    return [p]


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        selftest()
    else:
        main()
