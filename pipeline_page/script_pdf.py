"""Script PDF for the OF reference-style reel "It lives in the small things" (A4, Nunito, OF colours, frame per beat).
-> reel/organic_fostering/small_things_reference_style/organic_fostering_small_things_script.pdf"""
import os, base64, io, json
import cv2

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FR = f'{ROOT}/workspace_page/frames_ref'
OUT = f'{ROOT}/reel/organic_fostering/small_things_reference_style'
FON = f'{ROOT}/workspace_sol/fonts'

BEATS = [
    (1.8, '0:00', 'If you\'re thinking about fostering,', 'If you\'re / <b>Thinking</b> &nbsp;·&nbsp; About / <b class=l>Fostering</b>',
     'A field of small 3D houses; one hero house in front with its windows lit. Toned plum.', 'Opens out of a soft blur; the image arrives from defocus; each word sharpens in. Music fades up.'),
    (3.9, '0:02', 'you\'re probably picturing something big.', 'You\'re probably / <b>Picturing</b> / <b class=l>Something big</b>',
     'Grandparent and child walking (organicfostering.co.uk photo), plum-toned with feathered edges.', 'Whole-frame blur dissolve; soft whoosh.'),
    (6.0, '0:04', 'Most people imagine the big moments.', 'Most people imagine / <b>The big moments</b>',
     'Family on a garden bench (website photo), soft mist across the bottom.', 'Arrives from a giant out-of-focus close-up and pulls back sharp.'),
    (10.9, '0:07', 'A spare room. The paperwork. The training.', '✦ A spare room &nbsp;·&nbsp; ✦ The paperwork &nbsp;·&nbsp; ✦ The training',
     'A 3D open book (the paperwork). Star bullets in orange, green and magenta.', 'Each bullet pops in on its word; the list tilts slightly before the dissolve.'),
    (12.8, '0:11', 'But belonging doesn\'t live there.', 'But / <b>Belonging</b> / Doesn\'t live there.',
     'Two 3D houses on an ivory and lilac checker floor (the reference\'s chessboard).', 'Floor fades up, houses arrive from defocus.'),
    (14.6, '0:13', 'It lives in the small things.', 'It lives in / <b>The small</b> / <b class=l>Things</b>',
     'Overhead open book: household photos, the sky-blue scarf, "Match day", "3:00" - with a centre card for the words.', 'A white glow blooms from the centre and carries the cut.'),
    (16.4, '0:15', 'A name on the page.', '📌 <b>A name</b> / on the page',
     'A plum push pin drops above the words; the child\'s crayon drawing ("ME + JO") in full colour.', 'Pin drops in; text swaps by blur while the pin stays.'),
    (18.2, '0:17', 'A text when City score.', '<b>A text</b> / when City score',
     'Message pills: "B · GOAL", then "I KNOW" six frames later.', 'Pills slide in from each side with a pop.'),
    (19.8, '0:19', 'A drawing on the fridge.', '<b>A drawing</b> / on the fridge',
     'The 3D fridge slides in; its drawing and letter magnets stay in colour.', 'Slide with defocus; soft whoosh.'),
    (21.4, '0:20', 'When those are missing,', 'When &nbsp; those &nbsp; are / <b>Missing</b>',
     'Words only.', 'Small words appear one by one, then the big word.'),
    (22.9, '0:22', 'a bigger house doesn\'t fix it.', 'A bigger / <b>House</b> / <b class=l>Doesn\'t fix it</b>',
     'A giant out-of-focus house sweeps past the lens, then a house falls slowly towards its shadow.', 'Low whoosh, soft thud.'),
    (24.6, '0:23', 'Being noticed does.', 'Being noticed / <b>Does.</b>',
     'Two magenta 3D hearts, half off-frame (the reference\'s eye beat).', 'Hearts drift in from the corners.'),
    (27.5, '0:25', 'That\'s why we start small, and stay close.', 'That\'s why we / <b>Start small</b> &nbsp;→&nbsp; and / <b>Stay close</b>',
     'Words only.', 'The first pair blurs away and the second sharpens in.'),
    (31.5, '0:28', 'Organic Fostering.', 'Official logo · <b>Thinking about fostering in Greater Manchester?</b> · Start your enquiry · Link in bio · organicfostering.co.uk',
     'End card on ivory with the official Organic Fostering logo.', 'The ground sinks to lilac, a plum flash, the logo assembles out of a blur; chimes. Held to 0:34.'),
]


def thumb(t):
    im = cv2.imread(f'{FR}/{int(round(t * 25)):05d}.png')
    im = cv2.resize(im, (270, 480), interpolation=cv2.INTER_AREA)
    ok, b = cv2.imencode('.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 88])
    return 'data:image/jpeg;base64,' + base64.b64encode(b.tobytes()).decode()


def font(name, w, style='normal'):
    b = base64.b64encode(open(f'{FON}/{name}.ttf', 'rb').read()).decode()
    return f"@font-face{{font-family:Nunito;font-weight:{w};font-style:{style};src:url(data:font/ttf;base64,{b})}}"


rows = []
for i, (t, tc, vo, ons, vis, mot) in enumerate(BEATS):
    rows.append(f'''<div class=beat><img src="{thumb(t)}"><div class=txt>
<div class=hd><span class=tc>{tc}</span><span class=n>Beat {i + 1}</span></div>
<p class=vo>“{vo}”</p>
<p><span class=k>On screen</span><span>{ons}</span></p>
<p><span class=k>Visual</span><span>{vis}</span></p>
<p><span class=k>Motion &amp; sound</span><span>{mot}</span></p></div></div>''')

full = ' '.join(b[2] for b in BEATS)
html = f'''<!doctype html><html><head><meta charset=utf-8><style>
{font('Nunito-400', 400)}{font('Nunito-700', 700)}{font('Nunito-800', 800)}{font('Nunito-900', 900)}
@page{{size:A4;margin:16mm 14mm}}
body{{font-family:Nunito;color:#2B2B2B;font-size:10.5pt;margin:0}}
h1{{font-weight:900;color:#5B174F;font-size:26pt;margin:0 0 2mm}}
.sub{{color:#85727F;font-size:11pt;margin-bottom:6mm}}
.bar{{height:3mm;background:linear-gradient(90deg,#5B174F 0 25%,#B7006E 25% 50%,#FF6411 50% 75%,#61A80A 75%);border-radius:2mm;margin-bottom:6mm}}
.meta{{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm;margin-bottom:6mm}}
.meta div{{background:#FCF8F5;border:1px solid #EADFE6;border-radius:3mm;padding:3mm}}
.meta b{{display:block;color:#5B174F;font-size:9pt}}
h2{{color:#5B174F;font-weight:800;font-size:14pt;margin:6mm 0 3mm}}
.vofull{{background:#FCF8F5;border-left:2mm solid #5B174F;padding:4mm 5mm;font-size:12pt;line-height:1.55;border-radius:0 3mm 3mm 0}}
.beat{{display:flex;gap:6mm;padding:4mm 0;border-bottom:1px solid #EADFE6;break-inside:avoid}}
.beat img{{width:36mm;height:64mm;object-fit:cover;border-radius:2mm;box-shadow:0 1mm 3mm rgba(91,23,79,.25)}}
.txt{{flex:1}}
.hd{{display:flex;gap:3mm;align-items:center;margin-bottom:2mm}}
.tc{{background:#5B174F;color:#fff;font-weight:800;border-radius:2mm;padding:.6mm 2.4mm;font-size:9.5pt}}
.n{{color:#85727F;font-weight:700;font-size:9pt}}
.vo{{font-weight:800;font-size:13pt;color:#2B2B2B;margin:1mm 0 3mm}}
p{{margin:0 0 2mm;line-height:1.45}}
.txt p:not(.vo){{display:grid;grid-template-columns:32mm 1fr;column-gap:2mm}}
.k{{display:block;color:#B7006E;font-weight:800;font-size:8.5pt;text-transform:uppercase;letter-spacing:.04em}}
b{{color:#5B174F}} b.l{{color:#A48A9C}}
.notes li{{margin-bottom:1.6mm;line-height:1.45}}
.cap{{background:#FCF8F5;border:1px solid #EADFE6;border-radius:3mm;padding:4mm 5mm;line-height:1.55}}
</style></head><body>
<h1>It lives in the small things</h1>
<div class=sub>Organic Fostering · Instagram Reel script · after the Pinterest reference, in Organic Fostering colours</div>
<div class=bar></div>
<div class=meta><div><b>Format</b>9:16 · 1080 × 1920</div><div><b>Length</b>34 seconds · 25 fps</div>
<div><b>Voice</b>One narrator (en-GB)</div><div><b>Music</b>“Lasting Hope”, Kevin MacLeod</div></div>
<h2>Full voiceover</h2>
<div class=vofull>{full}</div>
<h2>Look</h2>
<p>Ivory ground with a soft plum vignette; the logo small at the top centre; plum chrome crescents turning slowly in the top-left and bottom-right corners. One cutout per beat, toned plum. Only the small things keep their real colour - the child’s drawing, the sky-blue scarf, the letter magnets, the hearts. Type: Nunito - a small light line over a big bold plum line (secondary big words in lilac); star bullets in orange, green and magenta. Every word sharpens out of a blur; every beat changes with a whole-frame blur dissolve.</p>
<h2>Beat by beat</h2>
{''.join(rows)}
<h2>Instagram caption</h2>
<div class=cap>Belonging rarely starts with the big moments. It starts with a name on a page, a text when City score, a drawing on the fridge. Thinking about fostering in Greater Manchester? Start your enquiry through the link in our bio.<br><br>#OrganicFostering #FosteringManchester #BecomeAFosterCarer</div>
<h2>Production notes</h2>
<ul class=notes>
<li>Narration: AI-generated voice (Microsoft neural “Ryan”, en-GB). Disclose AI voice where the platform asks. Can be re-voiced with ElevenLabs once credits reset.</li>
<li>Photos: organicfostering.co.uk, toned plum. 3D (houses, book, pin, fridge, hearts, corner crescents): rendered in Blender.</li>
<li>Music: “Lasting Hope” by Kevin MacLeod (incompetech.com), licensed under CC BY 4.0 - credit when posting. Sound effects synthesised.</li>
<li>Brand: Nunito, plum #5B174F, magenta #B7006E, orange #FF6411, green #61A80A, ivory #FCF8F5; official logo unmodified; no exclamation marks.</li>
<li>Delivery: H.264 + AAC stereo, −14 LUFS. Files: organic_fostering_small_things.mp4 (master) and _share.mp4.</li>
</ul>
</body></html>'''
open(f'{OUT}/script.html', 'w').write(html)

import subprocess
js = f"""const {{ chromium }} = require('playwright');
(async () => {{ const b = await chromium.launch(); const p = await b.newPage();
await p.goto('file://{OUT}/script.html'); await p.waitForTimeout(600);
await p.pdf({{ path: '{OUT}/organic_fostering_small_things_script.pdf', format: 'A4', printBackground: true,
  margin: {{ top: '16mm', bottom: '16mm', left: '14mm', right: '14mm' }} }});
await b.close(); }})();"""
subprocess.run(['node', '-e', js], check=True)
os.remove(f'{OUT}/script.html')
print('pdf written')
