"""assets3d_gpu.py - pick the Cycles render device for the Blender builders (assets3d_*.py).

Default is CPU (this container has no GPU). On a PC with a graphics card:

    FOSTER_GPU=1 python3 assets3d_icons.py all     # OPTIX > CUDA > HIP > METAL > ONEAPI, else CPU

FOSTER_GPU_TYPE=CUDA forces one backend (useful if OPTIX misbehaves on an older driver).
Renders are the same on either device apart from sampling noise, which OIDN removes; the fixed seed
keeps frames stable within a sequence, so never mix CPU and GPU frames inside one asset folder.
"""
import os

_BACKENDS = ('OPTIX', 'CUDA', 'HIP', 'METAL', 'ONEAPI')
_reported = False


def wants_gpu():
    """True when FOSTER_GPU is set to anything but '' / '0'.  e.g. wants_gpu() -> False"""
    return os.environ.get('FOSTER_GPU', '0').strip() not in ('', '0', 'false', 'no')


def set_device(bpy, sc):
    """Point scene `sc` at the GPU when FOSTER_GPU=1 and one is usable; returns the backend used.
    Call it after read_factory_settings (which resets the preferences).  e.g. set_device(bpy, sc) -> 'CPU'"""
    global _reported
    used = 'CPU'
    sc.cycles.device = 'CPU'
    if wants_gpu():
        order = (os.environ['FOSTER_GPU_TYPE'].upper(),) if os.environ.get('FOSTER_GPU_TYPE') else _BACKENDS
        try:
            prefs = bpy.context.preferences.addons['cycles'].preferences
            for kind in order:
                try:
                    prefs.compute_device_type = kind
                    prefs.get_devices()
                except Exception:
                    continue
                devs = [d for d in prefs.devices if d.type == kind]
                if not devs:
                    continue
                for d in prefs.devices:
                    d.use = d.type == kind
                sc.cycles.device = 'GPU'
                used = kind + ':' + ','.join(d.name for d in devs)
                break
        except Exception as e:          # no cycles add-on prefs (stripped bpy build): stay on CPU
            used = f'CPU (GPU unavailable: {e})'
        if used == 'CPU':
            used = 'CPU (FOSTER_GPU=1 but no GPU backend found)'
    if not _reported:
        print(f'[assets3d] Cycles device: {used}', flush=True)
        _reported = True
    return used
