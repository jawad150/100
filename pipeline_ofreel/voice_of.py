"""Narration for OF Closer than you think (edge-tts en-GB Sonia): trims each line, lays the lines out scene by scene, and
writes workspace_ofreel/tts/vo.wav + info.json with the scene starts and the word times the reel syncs to."""
import os, json, subprocess
import numpy as np
import soundfile as sf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
T = f'{ROOT}/workspace_ofreel/tts'
SR = 48000


def load(n):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{T}/{n}.mp3', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                                        capture_output=True, check=True).stdout, np.float32)


def trim(x, thr=0.008):
    idx = np.where(np.abs(x) > thr)[0]
    return x[max(0, idx[0] - int(0.02 * SR)):min(len(x), idx[-1] + int(0.08 * SR))]


# (scene that starts before this line or None, lead-in after the scene start, line id)
PLAN = [('s1', 0.5, 'v1'), ('s2', 0.75, 'v2'), ('s3', 0.35, 'v3'), ('s4', 0.45, 'v4'), ('s5', 0.35, 'v5'), ('s6', 0.35, 'v6'),
        ('end', 0.45, 'v7')]
SCENE_GAP = 0.3                                                         # breath between a line ending and the next cut

if __name__ == '__main__':
    from faster_whisper import WhisperModel
    m = WhisperModel('small.en', device='cpu', compute_type='int8')
    t = 0.0
    scenes, lines, words = {}, {}, []
    clips = []
    for sc, lead, lid in PLAN:
        x = trim(load(lid))
        if sc is not None:
            if sc != 's1':
                t += SCENE_GAP
            scenes[sc] = round(t, 3)
        t += lead
        clips.append((t, x))
        segs, _ = m.transcribe(x[::3].copy(), word_timestamps=True, beam_size=5)
        ws = [(w.word.strip(), round(w.start + t, 3), round(w.end + t, 3), lid) for s in segs for w in s.words]
        words += ws
        lines[lid] = (round(t, 3), round(t + len(x) / SR, 3))
        print(lid, f'{t:.2f}-{t + len(x) / SR:.2f}', ' '.join(f'{w}@{a:.2f}' for w, a, b, _ in ws))
        t += len(x) / SR
    dur = round(t + 1.5, 2)
    out = np.zeros(int(dur * SR), np.float32)
    for t0, x in clips:
        i0 = int(t0 * SR)
        out[i0:i0 + len(x)] += x
    sf.write(f'{T}/vo.wav', out, SR)
    json.dump({'scenes': scenes, 'lines': lines, 'words': words, 'dur': dur}, open(f'{T}/info.json', 'w'), indent=1)
    print('scenes', scenes, 'dur', dur)
