"""Download the CC0 Poly Haven HDRIs, PBR textures and props used by the Yaadein plates.

python3 fetch_assets.py   ->  workspace2/assets/ph/{hdri,tex,model}/<id>/...
"""
import concurrent.futures as cf
import json
import os
import urllib.request

ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'workspace2', 'assets', 'ph')

HDRIS = ['rooftop_night', 'shanghai_bund', 'modern_buildings_night', 'the_sky_is_on_fire',
         'kloppenheim_06_puresky', 'sunset_jhbcentral', 'grasslands_sunset', 'evening_road_01_puresky']
TEXTURES = ['concrete_floor_worn_001', 'brick_wall_001', 'asphalt_02', 'brown_mud_leaves_01', 'grass_path_2',
            'rusty_metal_02', 'dark_wooden_planks', 'concrete_wall_008', 'forest_ground_04']
MODELS = ['rusted_spade_01', 'wooden_crate_02', 'vintage_suitcase', 'postcard_set_01', 'standing_picture_frame_01',
          'exterior_aircon_unit', 'modular_airduct_rectangular_01', 'modular_electric_cables', 'security_light',
          'street_lamp_01', 'power_box_01', 'concrete_road_barrier', 'tree_stump_01', 'island_tree_02',
          'grass_medium_01', 'Camera_01', 'pocket_watch', 'treasure_chest', 'wooden_lantern_01',
          'modular_fire_escape', 'jacaranda_tree', 'dead_tree_trunk']


def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': 'yaadein-reel/1.0'})
    with urllib.request.urlopen(req, timeout=300) as r, open(path + '.part', 'wb') as f:
        f.write(r.read())
    os.replace(path + '.part', path)


def files(asset):
    req = urllib.request.Request('https://api.polyhaven.com/files/' + asset, headers={'User-Agent': 'yaadein-reel/1.0'})
    return json.load(urllib.request.urlopen(req, timeout=60))


def jobs():
    for a in HDRIS:
        f = files(a)['hdri']
        res = '4k' if '4k' in f else sorted(f)[-1]
        yield f[res]['hdr']['url'], os.path.join(ROOT, 'hdri', a + '.hdr')
    for a in TEXTURES:
        f = files(a)
        for m in ('Diffuse', 'nor_gl', 'Rough', 'AO', 'Displacement'):
            if m in f and '2k' in f[m]:
                fmt = 'jpg' if 'jpg' in f[m]['2k'] else 'png'
                yield f[m]['2k'][fmt]['url'], os.path.join(ROOT, 'tex', a, m + '.' + fmt)
    for a in MODELS:
        g = files(a)['gltf']
        g = g['2k' if '2k' in g else sorted(g)[0]]['gltf']
        yield g['url'], os.path.join(ROOT, 'model', a, a + '.gltf')
        for rel, inc in g.get('include', {}).items():
            yield inc['url'], os.path.join(ROOT, 'model', a, rel)


if __name__ == '__main__':
    todo = list(jobs())
    print(len(todo), 'files')
    with cf.ThreadPoolExecutor(8) as ex:
        for fut in cf.as_completed([ex.submit(get, u, p) for u, p in todo]):
            fut.result()
    print('done')
