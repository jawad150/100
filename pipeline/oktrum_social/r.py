import sys, os
sys.path.insert(0, sys.argv[1])
import assets3d_oktrum as A
name, variant, mode, frame, spp, sz = sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])
spec = A.ASSETS[name]
if not any(f[0] == variant and f[1] == mode for f in spec['folders']):
    n = [f[2] for f in spec['folders']][0]
    spec['folders'].append((variant, mode, n if mode != 'anim' else 48))
spec['size'] = (sz, sz)
A.render_asset(name, variant, mode, frames=[frame], samples=spp)
