"""Block until a file exists (or a deadline passes) without a shell `sleep` loop.
    python3 pipeline/jawad_reels/tools/wait_for.py <path> [max_seconds=580]
Exit 0 and print the file's first 4 KB when it exists; exit 1 on timeout (call it again to keep waiting)."""
import os
import sys
import time

path, limit = sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 580.0
t0 = time.time()
while not os.path.exists(path):
    if time.time() - t0 > limit:
        print('still waiting for', path, 'after %.0f s' % (time.time() - t0))
        sys.exit(1)
    time.sleep(10)
print(open(path, errors='replace').read(4096) if os.path.isfile(path) else path)
