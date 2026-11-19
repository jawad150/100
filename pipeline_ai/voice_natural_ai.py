"""Use the ElevenLabs take with its own pacing; insert extra air at chosen points; word timings from whisper, mapped
onto the script's words. -> workspace_ai/tts/vo.wav + info.json"""
import json, subprocess, sys
import numpy as np, soundfile as sf
from faster_whisper import WhisperModel
import timing_ai as T
take = sys.argv[1]
EXTRA = {'inside.': 0.5}                     # seconds of air added after these script words
sr = 44100
a = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', take, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
a16 = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', take, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
ws = [(w.word.strip(), w.start, w.end) for s in WhisperModel('small.en', device='cpu', compute_type='int8').transcribe(a16, word_timestamps=True, beam_size=5)[0] for w in s.words]
script = [w for text, _, _ in T.LINES for w in text.split()]
assert len(ws) == len(script), (len(ws), len(script))
out, words, shift, last = [], [], 0.0, 0
for (w, b, e), sw in zip(ws, script):
    words.append([sw, round(b + shift, 3), round(e + shift, 3)])
    if sw in EXTRA:
        cut = int((e + 0.08) * sr)
        out.append(a[last:cut]); out.append(np.zeros(int(EXTRA[sw] * sr), np.float32))
        last = cut; shift += EXTRA[sw]
out.append(a[last:])
y = np.concatenate(out)
sf.write(f'{T.S}/tts/vo.wav', y, sr)
json.dump({'placeholder': False, 'words': words, 'dur': len(y) / sr}, open(f'{T.S}/tts/info.json', 'w'), indent=0)
print('vo.wav', round(len(y) / sr, 2), 'last word ends', words[-1][2])
