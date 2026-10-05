"""Byte ranges of the frontal interview (C8948) video+audio samples around bite b1 (keyframe-aligned)."""
import bisect, json, struct, sys
sys.path.insert(0, ".")
import mp4index as M

HDR = "v916/srcV/_headers/C8948 (1).mov.hdr.mp4"
WANT = [(64.5, 77.5)]
buf = open(HDR, "rb").read()
mv = next(M.find(buf, 0, len(buf), ["moov"]))
sync = None
for ts, te in M.find(buf, mv[0], mv[1], ["trak"]):
    mdia = next(M.find(buf, ts, te, ["mdia"]))
    hs, he = next(M.find(buf, mdia[0], mdia[1], ["hdlr"]))
    if buf[hs + 8:hs + 12] == b"vide":
        stbl = next(M.find(buf, mdia[0], mdia[1], ["minf", "stbl"]))
        for typ, s, e in M.boxes(buf, stbl[0], stbl[1]):
            if typ == "stsd":
                print("codec:", buf[s + 12:s + 16])
            if typ == "stss":
                n = struct.unpack(">I", buf[s + 4:s + 8])[0]
                sync = [x - 1 for x in struct.unpack(f">{n}I", buf[s + 8:s + 8 + 4 * n])]
out = []
for tab in M.track_tables(buf):
    if tab["kind"] not in ("vide", "soun"):
        continue
    times = M.sample_times(tab)
    sizes = tab["sizes"]
    off = [0] * len(sizes)
    for coff, ln, si, n in M.chunk_spans(tab):
        o = coff
        for k in range(si, si + n):
            off[k] = o
            o += sizes[k]
    for t0, t1 in WANT:
        i0 = bisect.bisect_left(times, t0)
        if tab["kind"] == "vide" and sync:
            i0 = sync[max(0, bisect.bisect_right(sync, i0) - 1)]
        i1 = min(len(times) - 1, bisect.bisect_right(times, t1) + 8)
        out += [(off[i], off[i] + sizes[i]) for i in range(i0, i1 + 1)]
        print(tab["kind"], f"samples {i0}-{i1}  from {times[i0]:.2f}s", "all-intra" if (tab["kind"] == "vide" and not sync) else "")
out.sort()
merged = []
for s, e in out:
    if merged and s <= merged[-1][1] + 4096:
        merged[-1] = (merged[-1][0], max(e, merged[-1][1]))
    else:
        merged.append((s, e))
print(len(merged), "ranges", sum(e - s for s, e in merged) / 1e6, "MB")
json.dump({"C8948 (1).mov": merged}, open("v916/plan_front.json", "w"))
