"""Turntable renders (24 angles) of the recipe reel's 3D objects -> workspace_recipe/spin/<name>/NNN.png"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_nq'))
import blender_spin as BS
import blender_recipe as BR
ROOT = os.path.abspath(os.path.join(HERE, '..'))
BS.OUT = f'{ROOT}/workspace_recipe/spin'
BS.TOK = dict(BR.TOK)
if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    for n in (argv or list(BS.TOK)):
        if os.path.exists(f'{BS.OUT}/{n}/{BS.NFR - 1:03d}.png'):
            continue
        BS.spin_render(n)
