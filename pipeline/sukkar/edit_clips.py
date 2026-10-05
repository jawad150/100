"""Clip -> representative source times used in the edit (input for grade3.py's exposure match).

python3 edit_clips.py > look/edit_clips.json
"""
import json

import reel_sukkar as R

clips = {}
prev = 0.0
for end_s, spec, trans in R.TL:
    if spec.get("kind") == "broll":
        clip = spec["label"].split("@")[0]
        d = end_s - prev
        t = spec["t"] - (d if spec.get("reverse") else 0) + d / 2
        clips.setdefault(clip, []).append(round(max(0.2, t), 2))
    prev = end_s
print(json.dumps(clips))
