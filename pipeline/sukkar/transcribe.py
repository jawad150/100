"""Word-level transcript of a clip's audio with faster-whisper.

usage: python3 transcribe.py SRC OUT_PREFIX [channel]
writes OUT_PREFIX.json (segments + words) and OUT_PREFIX.txt (readable, timestamped)
"""
import json, subprocess, sys

import numpy as np
from faster_whisper import WhisperModel

src, out = sys.argv[1], sys.argv[2]
chan = sys.argv[3] if len(sys.argv) > 3 else "mix"
af = "pan=mono|c0=0.5*c0+0.5*c1" if chan == "mix" else f"pan=mono|c0=c{chan}"
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-map", "0:a:0", "-af", af, "-ar", "16000",
                      "-f", "f32le", "-"], capture_output=True, check=True).stdout
audio = np.frombuffer(raw, np.float32)
model = WhisperModel("small.en", device="cpu", compute_type="int8", download_root="models", cpu_threads=4)
segs, info = model.transcribe(audio, language="en", word_timestamps=True, beam_size=5,
                              vad_filter=True, condition_on_previous_text=False)
res = []
with open(out + ".txt", "w") as f:
    for s in segs:
        words = [{"w": w.word, "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 3)} for w in s.words]
        res.append({"s": round(s.start, 3), "e": round(s.end, 3), "text": s.text.strip(), "words": words})
        line = f"[{s.start:7.2f} - {s.end:7.2f}] {s.text.strip()}"
        f.write(line + "\n")
        print(line, flush=True)
json.dump(res, open(out + ".json", "w"), indent=0)
