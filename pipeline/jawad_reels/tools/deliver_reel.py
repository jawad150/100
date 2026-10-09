#!/usr/bin/env python3
"""deliver_reel.py - package one QA-passed @jawad_mp4 reel into reel/jawad_reels/<slug>/ (session 5 delivery step).

    python3 tools/deliver_reel.py <slug> --picture <render.py master mp4> --dur <s> --cover <s>
        --mix-a <A wav> --mix-b <B wav> --stem-vo <wav> --stem-sfx <wav> --stem-music <wav>
        --srt <srt> --caption <txt> [--minor "item" ...] [--qa "QA note"]

Makes (reel_s3.js "Deliver" spec; no preview mp4, every file < 95 MB, no Git LFS):
    workspace/jawad_reels/<slug>/master/<slug>_master_A.mp4 / _B.mp4   picture copied, epic_mix.mux (two-pass loudnorm
                                                                        linear, -14 LUFS, TP -1.5, AAC 320k 48 kHz)
    jawad_<slug>_ig.mp4            H.264 High 2-pass at the highest bitrate that keeps the file <= 90 MB (cap 20 Mbps),
                                   +faststart, version A audio (AAC 320k), 1080x1920, 30 fps
    jawad_<slug>_ig_songready.mp4  the same video stream with version B audio (VO + SFX only)
    jawad_<slug>_master.mp4        the CRF 14 master with A audio (re-encoded at CRF 14 -maxrate 20M if >= 94 MB)
    stems/jawad_<slug>_stem_{vo,sfx,music}.wav   48 kHz 24-bit, at the A mix's gains
    jawad_<slug>_cover.jpg (1080x1920, q 92) + jawad_<slug>_cover_grid_3x4.jpg (y 240-1680)
    jawad_<slug>_caption.txt, jawad_<slug>.srt, README.md (file table with measurements)
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
P = os.path.dirname(HERE)
sys.path.insert(0, P)
REPO = os.path.abspath(os.path.join(P, '..', '..'))

import epic_mix as M  # noqa: E402


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError('%s failed: %s' % (cmd[0], r.stderr[-800:]))
    return r


def probe(path):
    r = run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path])
    return json.loads(r.stdout)


def ebur(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True)
    s = r.stderr[r.stderr.rfind('Summary:'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))  # noqa: E731
    return dict(I=g('I'), LRA=g('LRA'), TP=g('Peak'))


def vinfo(path, dur):
    pr = probe(path)
    v = [s for s in pr['streams'] if s['codec_type'] == 'video'][0]
    a = [s for s in pr['streams'] if s['codec_type'] == 'audio']
    d = float(pr['format']['duration'])
    info = dict(size_mb=round(os.path.getsize(path) / 1e6, 2), w=v['width'], h=v['height'], fps=v['r_frame_rate'],
                vcodec='%s %s' % (v['codec_name'], v.get('profile', '')), pix=v['pix_fmt'], frames=int(v.get('nb_frames', 0)),
                dur=round(d, 3), vbr_mbps=round(int(v.get('bit_rate', 0)) / 1e6, 2),
                audio=('%s %s Hz %s kbps' % (a[0]['codec_name'], a[0]['sample_rate'], int(a[0].get('bit_rate', 0)) // 1000)
                       if a else 'none'))
    info['ok'] = (v['width'] == 1080 and v['height'] == 1920 and v['r_frame_rate'] == '30/1'
                  and abs(d - dur) <= 1 / 30 + 0.03 and info['size_mb'] < 95)
    if a:
        info['ebur128'] = ebur(path)
        e = info['ebur128']
        info['ok'] = info['ok'] and abs(e['I'] + 14) <= 0.5 and e['TP'] <= -1.5
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    for k in ('picture', 'mix-a', 'mix-b', 'stem-vo', 'stem-sfx', 'stem-music', 'srt', 'caption'):
        ap.add_argument('--' + k, required=True)
    ap.add_argument('--dur', type=float, required=True)
    ap.add_argument('--cover', type=float, required=True)
    ap.add_argument('--cover-png', help='use this rendered still (e.g. captions off) instead of a master frame')
    ap.add_argument('--minor', action='append', default=[])
    ap.add_argument('--qa', default='')
    a = ap.parse_args()
    S, dur = a.slug, a.dur
    W = os.path.join(REPO, 'workspace', 'jawad_reels', S)
    OUT = os.path.join(REPO, 'reel', 'jawad_reels', S)
    os.makedirs(os.path.join(OUT, 'stems'), exist_ok=True)
    os.makedirs(os.path.join(W, 'master'), exist_ok=True)
    B = os.path.join(OUT, 'jawad_%s' % S)
    rep = {}
    # 1. masters A / B: the picture's video stream copied, the final mixes muxed with two-pass loudnorm
    mA, mB = os.path.join(W, 'master', '%s_master_A.mp4' % S), os.path.join(W, 'master', '%s_master_B.mp4' % S)
    rep['mux_A'] = M.mux(a.picture, a.mix_a, mA, dur=dur)['ebur128']
    rep['mux_B'] = M.mux(a.picture, a.mix_b, mB, dur=dur)['ebur128']
    # 2. IG video stream: 2-pass at the highest bitrate that keeps the file <= 90 MB (audio 320k), capped at 20 Mbps
    vb = min(20.0, (90.0 * 8 / dur) * 0.97 - 0.33)
    tmp = tempfile.mkdtemp()
    pl, vid = os.path.join(tmp, 'pass'), os.path.join(tmp, 'ig_video.mp4')
    common = ['-c:v', 'libx264', '-preset', 'slow', '-b:v', '%.2fM' % vb, '-passlogfile', pl, '-profile:v', 'high',
              '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709']
    run(['nice', '-n', '10', 'ffmpeg', '-v', 'error', '-y', '-i', mA] + common + ['-pass', '1', '-an', '-f', 'null', '/dev/null'])
    run(['nice', '-n', '10', 'ffmpeg', '-v', 'error', '-y', '-i', mA] + common
        + ['-pass', '2', '-maxrate', '%.2fM' % (vb * 1.4), '-bufsize', '%.2fM' % (vb * 2), '-an', vid])
    for name, src in (('ig', mA), ('ig_songready', mB)):
        run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', src, '-map', '0:v', '-map', '1:a', '-c', 'copy',
             '-movflags', '+faststart', '%s_%s.mp4' % (B, name)])
    shutil.rmtree(tmp, ignore_errors=True)
    # 3. master
    if os.path.getsize(mA) < 94e6:
        shutil.copyfile(mA, B + '_master.mp4')
        rep['master_note'] = 'CRF 14 master copied as is'
    else:
        run(['nice', '-n', '10', 'ffmpeg', '-v', 'error', '-y', '-i', mA, '-c:v', 'libx264', '-preset', 'slow', '-crf', '14',
             '-maxrate', '20M', '-bufsize', '40M', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709',
             '-color_trc', 'bt709', '-colorspace', 'bt709', '-c:a', 'copy', '-movflags', '+faststart', B + '_master.mp4'])
        rep['master_note'] = 'CRF 14 master was >= 94 MB: re-encoded at CRF 14 -maxrate 20M -bufsize 40M'
    # 4. stems (24-bit 48 kHz as rendered)
    stems = {}
    for k, src in (('vo', a.stem_vo), ('sfx', a.stem_sfx), ('music', a.stem_music)):
        dst = os.path.join(OUT, 'stems', 'jawad_%s_stem_%s.wav' % (S, k))
        run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-c:a', 'pcm_s24le', '-ar', '48000', dst])
        stems[k] = dict(file=os.path.relpath(dst, OUT), size_mb=round(os.path.getsize(dst) / 1e6, 2), ebur128=ebur(dst))
    rep['stems'] = stems
    # 5. cover
    if a.cover_png:
        run(['ffmpeg', '-v', 'error', '-y', '-i', a.cover_png, '-q:v', '2', B + '_cover.jpg'])
    else:
        run(['ffmpeg', '-v', 'error', '-y', '-ss', '%.4f' % (a.cover + 0.5 / 30), '-i', mA, '-frames:v', '1', '-q:v', '2',
             B + '_cover.jpg'])
    run(['ffmpeg', '-v', 'error', '-y', '-i', B + '_cover.jpg', '-vf', 'crop=1080:1440:0:240', '-q:v', '2',
         B + '_cover_grid_3x4.jpg'])
    # 6. text
    shutil.copyfile(a.caption, B + '_caption.txt')
    shutil.copyfile(a.srt, B + '.srt')
    run(['ffprobe', '-v', 'error', '-i', B + '.srt'])
    # 7. verify + README
    vids = {n: vinfo('%s%s.mp4' % (B, n), dur) for n in ('_ig', '_ig_songready', '_master')}
    rep['videos'] = vids
    rows = []
    what = {'_ig': 'Instagram Reels upload (version A: VO + SFX + original music)',
            '_ig_songready': 'same picture, version B audio (VO + SFX only): add a trending song in-app',
            '_master': 'CRF 14 master, version A audio'}
    for n, v in vids.items():
        e = v.get('ebur128', {})
        rows.append('| `jawad_%s%s.mp4` | %.1f MB | %s | %dx%d %s fps, %s %.1f Mbps, %s; %.3f s; %.1f LUFS, LRA %.1f, TP %.1f dBTP |'
                    % (S, n, v['size_mb'], what[n], v['w'], v['h'], v['fps'].split('/')[0], v['vcodec'].strip(), v['vbr_mbps'],
                       v['audio'], v['dur'], e.get('I', 0), e.get('LRA', 0), e.get('TP', 0)))
    for k, st in stems.items():
        e = st['ebur128']
        rows.append('| `%s` | %.1f MB | %s stem at the A mix gains (48 kHz 24-bit) | %.1f LUFS, TP %.1f dBTP |'
                    % (st['file'], st['size_mb'], k.upper() if k == 'vo' else k, e['I'], e['TP']))
    for f, w in (('_cover.jpg', 'cover frame %.2f s (1080x1920)' % a.cover), ('_cover_grid_3x4.jpg', '3:4 profile-grid crop (y 240-1680)'),
                 ('_caption.txt', 'IG caption, comment prompt, hashtags, AI info note'), ('.srt', 'Roman Urdu captions (SRT)')):
        rows.append('| `jawad_%s%s` | %.1f KB | %s | |' % (S, f, os.path.getsize(B + f) / 1e3, w))
    ok = all(v['ok'] for v in vids.values())
    with open(os.path.join(OUT, 'README.md'), 'w') as f:
        f.write('# @jawad_mp4 reel: %s\n\n%s\n\n| file | size | what it is | measured |\n|---|---|---|---|\n%s\n\n'
                % (S, a.qa or 'QA passed.', '\n'.join(rows)))
        f.write('All videos 1080x1920, 30 fps, duration %.3f s +- 1 frame, -14 LUFS +- 0.5, TP <= -1.5 dBTP: %s. %s.\n'
                % (dur, 'PASS' if ok else 'CHECK', rep['master_note']))
        if a.minor:
            f.write('\nKnown minor items (listed, not re-rendered; LEAD_DECISIONS 7):\n\n' + ''.join('- %s\n' % m for m in a.minor))
    with open(os.path.join(W, 'master', 'deliver_report.json'), 'w') as f:
        json.dump(rep, f, indent=1)
    print(json.dumps(dict(ok=ok, videos=vids, stems=stems, master_note=rep['master_note']), indent=1))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
