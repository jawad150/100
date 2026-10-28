"""Inject the works manifest into the site template -> workspace_pf/site/index.html"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', 'workspace_pf'))
works = json.load(open(f'{WS}/site/works.json'))
for w in works:
    for m in w['media']:
        m.pop('stills', None)
tpl = open(f'{HERE}/site_template2.html').read()
html = tpl.replace('/*WORKS*/[]', json.dumps(works, ensure_ascii=False))
open(f'{WS}/site/index.html', 'w').write(html)
print('wrote', len(html), 'bytes')
