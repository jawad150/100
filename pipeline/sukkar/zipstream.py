"""Streaming reader for Dropbox folder zips.

Dropbox writes large files as *stored* entries with a trailing data descriptor,
which normal streaming unzippers refuse. We find the end of each stored entry by
scanning for the descriptor signature and checking that its CRC and size match
the bytes seen so far.

usage: curl ... | python3 zipstream.py OUTDIR [regex-of-names-to-save]
Every entry is listed. Entries matching the regex are written to OUTDIR.
For MP4/MOV entries that are not saved, the ftyp+moov boxes are kept as
OUTDIR/_headers/<name>.hdr.mp4 so ffprobe can read duration and streams.
"""
import bisect, json, os, re, struct, sys, time, zlib

SIG_LFH = b"PK\x03\x04"
SIG_CDH = b"PK\x01\x02"
SIG_DD = b"PK\x07\x08"


class Stream:
    def __init__(self, f):
        self.f = f
        self.buf = bytearray()
        self.eof = False
        self.total = 0

    def fill(self, n):
        while len(self.buf) < n and not self.eof:
            b = self.f.read(1 << 22)
            if not b:
                self.eof = True
                break
            self.total += len(b)
            self.buf += b
        return len(self.buf) >= n

    def take(self, n):
        if not self.fill(n):
            raise EOFError
        out = bytes(self.buf[:n])
        del self.buf[:n]
        return out


class Mp4Header:
    """Tracks top-level MP4 boxes and keeps ftyp + moov."""

    def __init__(self):
        self.pos = 0        # file offset of the next byte fed
        self.next_box = 0   # file offset of the next top-level box header
        self.hdr = bytearray()
        self.keep = (0, 0)
        self.kept = bytearray()
        self.boxes = []

    def feed(self, data):
        mv = memoryview(data)
        i, L = 0, len(data)
        while i < L:
            off = self.pos + i
            if off < self.next_box:
                k = min(L - i, self.next_box - off)
                a, b = self.keep
                lo, hi = max(off, a), min(off + k, b)
                if lo < hi:
                    self.kept += mv[i + lo - off:i + hi - off]
                i += k
                continue
            want = 8 if len(self.hdr) < 8 else 16
            take = min(want - len(self.hdr), L - i)
            self.hdr += mv[i:i + take]
            i += take
            if len(self.hdr) < 8:
                continue
            size, typ = struct.unpack(">I4s", bytes(self.hdr[:8]))
            if size == 1 and len(self.hdr) < 16:
                continue
            if size == 1:
                size = struct.unpack(">Q", bytes(self.hdr[8:16]))[0]
            start = self.next_box
            hl = len(self.hdr)
            self.next_box = start + size if size >= 8 else 1 << 62
            self.boxes.append((typ.decode("latin1"), start, size))
            if typ in (b"ftyp", b"moov") and 8 <= size < (256 << 20):
                self.kept += self.hdr
                self.keep = (start + hl, start + size)
            self.hdr = bytearray()
        self.pos += L


def main():
    outdir = sys.argv[1]
    pat = re.compile(sys.argv[2], re.I) if len(sys.argv) > 2 and sys.argv[2] else None
    sparse = {}
    if len(sys.argv) > 3:
        import json, bisect
        sparse = {k: [tuple(r) for r in v] for k, v in json.load(open(sys.argv[3])).items()}
    os.makedirs(os.path.join(outdir, "_headers"), exist_ok=True)
    s = Stream(sys.stdin.buffer)
    t0 = time.time()
    count = 0
    while True:
        if not s.fill(4):
            break
        sig = bytes(s.buf[:4])
        if sig != SIG_LFH:
            if sig == SIG_CDH:
                print(f"[central directory reached] streamed={s.total/1e9:.2f} GB", flush=True)
            else:
                print(f"[unexpected signature {sig!r}]", flush=True)
            break
        h = s.take(30)
        (_, ver, flags, method, mt, md, crc, csz, usz, nl, el) = struct.unpack("<IHHHHHIIIHH", h)
        name = s.take(nl).decode("utf8", "replace")
        extra = s.take(el)
        zip64 = False
        j = 0
        while j + 4 <= len(extra):
            hid, ln = struct.unpack("<HH", extra[j:j + 4])
            if hid == 1:
                zip64 = True
            j += 4 + ln
        key = name.lstrip("/")
        want = sparse.get(key)
        save = (pat is not None and pat.search(name) and not name.endswith("/")) or want is not None
        is_mp4 = name.lower().endswith((".mp4", ".mov", ".m4v"))
        fh = None
        if save:
            path = os.path.join(outdir, key)
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            fh = open(path, "wb")
        mp4 = Mp4Header() if (is_mp4 and (not save or want is not None)) else None
        wstarts = [r[0] for r in want] if want else []
        fpos = [0]

        def sparse_write(chunk, p0):
            """Write bytes outside mdat payloads, and inside them only the wanted ranges."""
            p1 = p0 + len(chunk)
            skip = [(s + 16, s + size) for (t, s, size) in mp4.boxes if t == "mdat" and size > 16]
            # build keep segments = [p0,p1) minus skip, plus wanted
            segs = [(p0, p1)]
            for a, b in skip:
                nxt = []
                for s, e in segs:
                    if b <= s or a >= e:
                        nxt.append((s, e))
                        continue
                    if s < a:
                        nxt.append((s, a))
                    if b < e:
                        nxt.append((b, e))
                segs = nxt
            i = max(0, bisect.bisect_right(wstarts, p0) - 1)
            while i < len(want) and want[i][0] < p1:
                a, b = max(want[i][0], p0), min(want[i][1], p1)
                if a < b:
                    segs.append((a, b))
                i += 1
            for s, e in segs:
                fh.seek(s)
                fh.write(chunk[s - p0:e - p0])

        def emit(chunk):
            if mp4:
                mp4.feed(chunk)
            if fh:
                if want is not None:
                    sparse_write(chunk, fpos[0])
                else:
                    fh.write(chunk)
            fpos[0] += len(chunk)

        n = 0
        if method == 8:
            d = zlib.decompressobj(-15)
            while not d.eof:
                if not s.fill(1):
                    raise EOFError(name)
                chunk = bytes(s.buf)
                s.buf = bytearray()
                out = d.decompress(chunk)
                n += len(out)
                emit(out)
                if d.eof:
                    s.buf = bytearray(d.unused_data) + s.buf
        elif method == 0 and not (flags & 8):
            left = csz
            while left:
                s.fill(min(left, 1 << 22))
                k = min(left, len(s.buf))
                chunk = bytes(s.buf[:k])
                del s.buf[:k]
                emit(chunk)
                n += k
                left -= k
        elif method == 0:
            running = 0
            while True:
                s.fill(1 << 22)
                if not s.buf and s.eof:
                    raise EOFError(name)
                found = -1
                start = 0
                while True:
                    p = s.buf.find(SIG_DD, start)
                    if p < 0:
                        break
                    if not s.fill(p + 24):
                        pass
                    tail = bytes(s.buf[p + 4:p + 24])
                    pcrc = zlib.crc32(s.buf[:p], running) & 0xFFFFFFFF
                    size_here = n + p
                    c = struct.unpack("<I", tail[:4])[0]
                    if zip64 and len(tail) >= 20:
                        cs = struct.unpack("<Q", tail[4:12])[0]
                    else:
                        cs = struct.unpack("<I", tail[4:8])[0]
                    if c == pcrc and cs == size_here:
                        found = p
                        break
                    start = p + 1
                if found >= 0:
                    chunk = bytes(s.buf[:found])
                    emit(chunk)
                    n += len(chunk)
                    del s.buf[:found]
                    break
                keep = 3
                k = max(0, len(s.buf) - keep)
                chunk = bytes(s.buf[:k])
                running = zlib.crc32(chunk, running)
                emit(chunk)
                n += k
                del s.buf[:k]
        else:
            raise ValueError(f"unsupported method {method} for {name}")
        if flags & 8:
            if bytes(s.buf[:4]) == SIG_DD or (s.fill(4) and bytes(s.buf[:4]) == SIG_DD):
                s.take(4)
            s.take(20 if zip64 else 12)
        if fh:
            fh.close()
        if mp4 and mp4.kept and want is None:
            hp = os.path.join(outdir, "_headers", name.lstrip("/").replace("/", "__") + ".hdr.mp4")
            with open(hp, "wb") as g:
                g.write(mp4.kept)
        count += 1
        tag = "SAVED" if save else ""
        print(f"{n/1e9:9.3f} GB  {name}  {tag}  (t={time.time()-t0:.0f}s, {s.total/1e9:.1f} GB streamed)", flush=True)
    print(f"DONE entries={count}", flush=True)


if __name__ == "__main__":
    main()
