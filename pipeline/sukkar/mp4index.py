"""Read sample tables from an MP4/MOV moov box and compute byte ranges per track.

ranges(header_path, kind='soun', t_ranges=None) -> sorted list of (start, end) file offsets
covering every chunk of the first track of that handler kind (optionally only chunks
overlapping the given (t0, t1) second ranges).
"""
import struct


def boxes(buf, off, end):
    while off + 8 <= end:
        size, typ = struct.unpack(">I4s", buf[off:off + 8])
        hl = 8
        if size == 1:
            size = struct.unpack(">Q", buf[off + 8:off + 16])[0]
            hl = 16
        elif size == 0:
            size = end - off
        yield typ.decode("latin1"), off + hl, off + size
        off += size


def find(buf, off, end, path):
    for typ, s, e in boxes(buf, off, end):
        if typ == path[0]:
            if len(path) == 1:
                yield s, e
            else:
                yield from find(buf, s, e, path[1:])


def track_tables(buf):
    moov = next(find(buf, 0, len(buf), ["moov"]))
    out = []
    for ts, te in find(buf, moov[0], moov[1], ["trak"]):
        mdia = next(find(buf, ts, te, ["mdia"]))
        hs, he = next(find(buf, mdia[0], mdia[1], ["hdlr"]))
        kind = buf[hs + 8:hs + 12].decode("latin1")
        ms, me = next(find(buf, mdia[0], mdia[1], ["mdhd"]))
        ver = buf[ms]
        if ver == 1:
            timescale = struct.unpack(">I", buf[ms + 20:ms + 24])[0]
        else:
            timescale = struct.unpack(">I", buf[ms + 12:ms + 16])[0]
        stbl = next(find(buf, mdia[0], mdia[1], ["minf", "stbl"]))
        tab = {"kind": kind, "timescale": timescale}
        for typ, s, e in boxes(buf, stbl[0], stbl[1]):
            if typ == "stco":
                n = struct.unpack(">I", buf[s + 4:s + 8])[0]
                tab["chunks"] = list(struct.unpack(f">{n}I", buf[s + 8:s + 8 + 4 * n]))
            elif typ == "co64":
                n = struct.unpack(">I", buf[s + 4:s + 8])[0]
                tab["chunks"] = list(struct.unpack(f">{n}Q", buf[s + 8:s + 8 + 8 * n]))
            elif typ == "stsc":
                n = struct.unpack(">I", buf[s + 4:s + 8])[0]
                tab["stsc"] = [struct.unpack(">III", buf[s + 8 + 12 * i:s + 20 + 12 * i]) for i in range(n)]
            elif typ == "stsz":
                fixed, n = struct.unpack(">II", buf[s + 4:s + 12])
                tab["sizes"] = [fixed] * n if fixed else list(struct.unpack(f">{n}I", buf[s + 12:s + 12 + 4 * n]))
            elif typ == "stts":
                n = struct.unpack(">I", buf[s + 4:s + 8])[0]
                tab["stts"] = [struct.unpack(">II", buf[s + 8 + 8 * i:s + 16 + 8 * i]) for i in range(n)]
        out.append(tab)
    return out


def chunk_spans(tab):
    """[(offset, length, first_sample_index, n_samples)] per chunk."""
    chunks, stsc, sizes = tab["chunks"], tab["stsc"], tab["sizes"]
    spans = []
    si = 0
    for ci in range(len(chunks)):
        cnum = ci + 1
        spc = 0
        for j, (first, per, _) in enumerate(stsc):
            nxt = stsc[j + 1][0] if j + 1 < len(stsc) else 1 << 62
            if first <= cnum < nxt:
                spc = per
                break
        length = sum(sizes[si:si + spc])
        spans.append((chunks[ci], length, si, spc))
        si += spc
    return spans


def sample_times(tab):
    t = []
    acc = 0
    for count, delta in tab["stts"]:
        for _ in range(count):
            t.append(acc / tab["timescale"])
            acc += delta
    return t


def ranges(header_path, kind="soun", t_ranges=None, pad=0):
    buf = open(header_path, "rb").read()
    # header file is ftyp + moov concatenated; parse the moov part
    tabs = [t for t in track_tables(buf) if t["kind"] == kind]
    out = []
    for tab in tabs[:1]:
        spans = chunk_spans(tab)
        times = sample_times(tab) if t_ranges else None
        for off, ln, si, n in spans:
            if t_ranges:
                t0 = times[si] if si < len(times) else 0
                t1 = times[min(si + n, len(times) - 1)]
                if not any(t1 >= a and t0 <= b for a, b in t_ranges):
                    continue
            out.append((max(0, off - pad), off + ln + pad))
    out.sort()
    merged = []
    for s, e in out:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(e, merged[-1][1]))
        else:
            merged.append((s, e))
    return merged


if __name__ == "__main__":
    import sys
    for kind in ("vide", "soun"):
        r = ranges(sys.argv[1], kind)
        print(kind, len(r), "ranges", sum(e - s for s, e in r) / 1e6, "MB")
