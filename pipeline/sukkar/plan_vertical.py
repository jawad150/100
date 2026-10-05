"""Byte ranges of the vertical interview's video samples for the on-camera bites (keyframe-aligned)."""
import json, struct, sys
sys.path.insert(0, ".")
import mp4index as M

SRC = "src/C8950 V2 (1).mp4"
WANT = [(62.5, 73.5), (381.5, 393.5), (440.0, 450.0)]


def read_moov(path):
    with open(path, "rb") as f:
        off = 0
        f.seek(0, 2); end = f.tell()
        while off < end:
            f.seek(off)
            h = f.read(16)
            size, typ = struct.unpack(">I4s", h[:8])
            if size == 1:
                size = struct.unpack(">Q", h[8:16])[0]
            if typ == b"moov":
                f.seek(off)
                return f.read(size), off
            off += size
    raise RuntimeError("no moov")


moov, moov_off = read_moov(SRC)
buf = moov
tabs = M.track_tables(buf)
# sync samples + ctts for the video track
mv = next(M.find(buf, 0, len(buf), ["moov"]))
vt = None
for ts, te in M.find(buf, mv[0], mv[1], ["trak"]):
    mdia = next(M.find(buf, ts, te, ["mdia"]))
    hs, he = next(M.find(buf, mdia[0], mdia[1], ["hdlr"]))
    if buf[hs + 8:hs + 12] == b"vide":
        stbl = next(M.find(buf, mdia[0], mdia[1], ["minf", "stbl"]))
        for typ, s, e in M.boxes(buf, stbl[0], stbl[1]):
            if typ == "stss":
                n = struct.unpack(">I", buf[s + 4:s + 8])[0]
                sync = [x - 1 for x in struct.unpack(f">{n}I", buf[s + 8:s + 8 + 4 * n])]
vtab = next(t for t in tabs if t["kind"] == "vide")
times = M.sample_times(vtab)
spans = M.chunk_spans(vtab)
sizes = vtab["sizes"]
# per-sample offsets
off = [0] * len(sizes)
for coff, ln, si, n in spans:
    o = coff
    for k in range(si, si + n):
        off[k] = o
        o += sizes[k]
gaps = [b - a for a, b in zip(sync, sync[1:])]
print(f"video samples {len(sizes)}, keyframes {len(sync)}, GOP frames min/median/max {min(gaps)}/{sorted(gaps)[len(gaps)//2]}/{max(gaps)}")
import bisect
ranges = []
for t0, t1 in WANT:
    i0 = bisect.bisect_left(times, t0)
    k = bisect.bisect_right(sync, i0) - 1
    i0 = sync[max(k, 0)]
    i1 = min(len(times) - 1, bisect.bisect_right(times, t1) + 8)
    for i in range(i0, i1 + 1):
        ranges.append((off[i], off[i] + sizes[i]))
    print(f"  want {t0}-{t1}s -> samples {i0}-{i1} (from keyframe at {times[i0]:.2f}s)")
ranges.sort()
merged = []
for s, e in ranges:
    if merged and s <= merged[-1][1] + 4096:
        merged[-1] = (merged[-1][0], max(e, merged[-1][1]))
    else:
        merged.append((s, e))
print(f"{len(merged)} video ranges, {sum(e - s for s, e in merged) / 1e6:.0f} MB")
old = json.load(open("plan_pass2.json"))
plan = {"C8950 V2 (1).mp4": sorted([tuple(r) for r in old["C8950 V2 (1).mp4"]] + merged)}
json.dump(plan, open("v916/plan_vertical.json", "w"))
print("audio ranges kept:", len(old["C8950 V2 (1).mp4"]))
