"""Content PDF for the OF reel "Closer than you think" (FOOH + interface overlays + 3D), built before the reel.
-> reel/organic_fostering/closer_than_you_think/OF_closer_than_you_think_content.pdf"""
import os, base64, subprocess
import cv2

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BG = f'{ROOT}/workspace_ofreel/bgimg'
FON = f'{ROOT}/workspace_sol/fonts'
OUT = f'{ROOT}/reel/organic_fostering/closer_than_you_think'
os.makedirs(OUT, exist_ok=True)


def b64(p, mime):
    return f'data:{mime};base64,' + base64.b64encode(open(p, 'rb').read()).decode()


def thumb(name, w=300, h=533):
    im = cv2.imread(f'{BG}/{name}')
    ih, iw = im.shape[:2]
    sc = max(w / iw, h / ih)
    im = cv2.resize(im, (int(iw * sc) + 1, int(ih * sc) + 1), interpolation=cv2.INTER_AREA)
    y0, x0 = (im.shape[0] - h) // 2, (im.shape[1] - w) // 2
    im = im[y0:y0 + h, x0:x0 + w]
    ok, b = cv2.imencode('.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return 'data:image/jpeg;base64,' + base64.b64encode(b.tobytes()).decode()


def ff(w):
    return f"@font-face{{font-family:Nunito;font-weight:{w};src:url({b64(f'{FON}/Nunito-{w}.ttf', 'font/ttf')})}}"


BEATS = [
    ('0:00', 'img-033.jpg', 'The search', 'Somewhere near you, a child needs a safe place to land.',
     'Search bar types "foster carer near me". Line: What if the answer is <b>you</b>?',
     'A Greater Manchester street of red-brick terraces (brand photo, carer and child planting). Slow push in, light film grain.',
     'Opens on a soft blur. The search bar drops in and types letter by letter with a blinking cursor.', 'Keyboard taps, soft room tone, gentle music fades up.'),
    ('0:05', 'img-000.jpg', 'The pin drops', 'What if that place was your home?',
     'Result card: Organic Fostering · Greater Manchester · Rated Good by Ofsted.',
     'Golden-hour field, a family walking away. A giant 3D plum map pin with the OF emblem drops from the sky and lands in the grass (FOOH).',
     'Zoom-through the search result. Pin falls with motion blur, lands with a camera shake and dust; the result card slides up.', 'Whistle-down, a soft thud, dust settling.'),
    ('0:09', 'img-034.jpg', 'Could I do this?', 'You do not need to arrive with all the answers. A spare room, time and patience are a good start.',
     'Check cards pop one by one: A spare bedroom ✓ · Time and patience ✓ · All the answers ✗ (not needed).',
     'A carer reading with a child on the sofa (brand photo). Cards pop like review stars in the reference.',
     'Whip pan in. Each card pops with overshoot; ticks draw themselves in Grow green.', 'One soft pop per card.'),
    ('0:15', 'img-035.jpg', 'Matching that sees the whole child', 'We match children with carers who understand their culture, faith and language.',
     'Tags float up: Culture · Faith · Language · Relationships.',
     'Homework at the kitchen table (brand photo). A 3D orange paper aeroplane lifts off the notebook and loops through the room, leaving a plum trail (FOOH).',
     'Light-leak dissolve in. The plane flies with motion blur; its trail becomes the transition, sweeping the screen.', 'Paper rustle, a soft whoosh following the plane.'),
    ('0:21', 'img-029.jpg', 'The need', 'Right now, the UK needs six thousand more foster families.',
     'Counter rolls 0 to <b>6,000</b>: more foster families needed across the UK in the next 12 months. Source: The Fostering Network, 2026.',
     'An autumn walk, two carers and two children (brand photo), slow push.',
     'The plum trail wipes in; the counter slams and settles; the source line fades up.', 'Counter ticks speeding up, one soft hit at 6,000.'),
    ('0:26', 'img-033.jpg', 'We stay alongside you', 'We stay alongside you, with training, advice outside normal hours, and published allowances.',
     'Support cards slide in: Training · Advice outside normal hours · Published allowances · Rated Good by Ofsted.',
     'Back on the terraced street: carer and child planting (brand photo), now in warm light.',
     'Slide push in. Cards stack like the reference\'s "popular times" panel.', 'Soft UI swishes.'),
    ('0:32', None, 'Start your enquiry', 'Start your enquiry with Organic Fostering. It carries no obligation.',
     'Types: Room to grow, roots to keep. Search bar types organicfostering.co.uk; button: Start your enquiry; 0161 241 1332.',
     'Ivory end card with the full-colour logo, the leaf pattern and the three-colour bar (brand sign-off).',
     'A green circle wipe from the last tick. Cursor taps the button with a ripple. Held still to the end.', 'Click, music resolves, room tone.'),
]

rows = ''.join(f'''<div class=beat>{f'<img src="{thumb(img)}">' if img else '<div class=endph>END CARD<br><span>ivory · logo · Start your enquiry</span></div>'}<div class=bt>
<div class=hd><span class=tc>{tc}</span><span class=nm>{nm}</span></div>
<p class=vo>“{vo}”</p>
<div class=g><span class=k>On screen</span><span>{ons}</span><span class=k>Visual</span><span>{vis}</span>
<span class=k>Motion & transition</span><span>{mot}</span><span class=k>Sound</span><span>{snd}</span></div></div></div>''' for tc, img, nm, vo, ons, vis, mot, snd in BEATS)
vo_full = ' '.join(b[3] for b in BEATS)
logo = b64(f'{ROOT}/workspace_three/web/logo.png', 'image/png')

html = f'''<!doctype html><html><head><meta charset=utf-8><style>
{ff(400)}{ff(700)}{ff(800)}{ff(900)}
@page{{size:A4;margin:14mm}}
body{{font-family:Nunito;color:#321F35;font-size:10pt;margin:0}}
h1{{font-weight:800;letter-spacing:-.02em;color:#5B174F;font-size:30pt;margin:3mm 0 1mm;line-height:1.05}}
.s0{{color:#655563;font-size:11pt}}
.bar{{height:3mm;border-radius:2mm;margin:5mm 0;background:linear-gradient(90deg,#B7006E 0 33.3%,#FF6411 33.3% 66.6%,#61A80A 66.6%)}}
.meta{{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm;margin-bottom:4mm}}
.meta div{{background:#F6EAF3;border-radius:3mm;padding:3mm}} .meta b{{display:block;color:#B7006E;font-size:8pt;letter-spacing:.05em}}
h2{{color:#5B174F;font-weight:800;font-size:14pt;margin:6mm 0 3mm}}
p{{line-height:1.55;margin:0 0 2.5mm}}
.refs{{display:grid;grid-template-columns:repeat(3,1fr);gap:3mm}} .refs div{{background:#FCF8F5;border:1px solid #F6EAF3;border-radius:3mm;padding:3mm 3.5mm;line-height:1.45}}
.refs b{{display:block;color:#5B174F;margin-bottom:1mm}}
.beat{{display:grid;grid-template-columns:34mm 1fr;gap:5mm;padding:4mm 0;border-bottom:1px solid #F6EAF3;break-inside:avoid}}
.beat img,.endph{{width:34mm;height:60.4mm;object-fit:cover;border-radius:3mm}}
.endph{{background:#FCF8F5;border:1px solid #E9DCE5;display:flex;flex-direction:column;align-items:center;justify-content:center;font-weight:800;color:#5B174F;font-size:9pt;text-align:center}}
.endph span{{font-weight:400;font-size:7.5pt;color:#655563;margin-top:1mm}}
.hd{{display:flex;gap:3mm;align-items:center;margin-bottom:1mm}} .tc{{background:#5B174F;color:#fff;font-weight:800;border-radius:2mm;padding:.4mm 2mm;font-size:8.5pt}}
.nm{{font-weight:800;font-size:11pt}} .vo{{font-weight:700;font-size:11pt;color:#5B174F;margin:1mm 0 2mm}}
.g{{display:grid;grid-template-columns:30mm 1fr;column-gap:2mm;row-gap:1.4mm;line-height:1.42}}
.k{{color:#B7006E;font-weight:800;font-size:7.8pt;text-transform:uppercase;letter-spacing:.05em;padding-top:.3mm}}
.vofull{{background:#F6EAF3;border-radius:3mm;padding:4mm 5mm;line-height:1.6;font-size:11pt}}
ul{{margin:0;padding-left:5mm}} li{{margin-bottom:1.6mm;line-height:1.45}}
.cap{{background:#FCF8F5;border-left:1.5mm solid #5B174F;padding:3.5mm 4.5mm;border-radius:0 2mm 2mm 0;line-height:1.55}}
.pb{{page-break-before:always}}
.small li{{font-size:8.8pt}}
</style></head><body>
<img src="{logo}" style="width:52mm">
<div class=bar></div>
<div class=s0>INSTAGRAM REEL · CONTENT PLAN · NOVEMBER 2026</div>
<h1>Closer than you think</h1>
<div class=s0>A child who needs a safe place to land may be closer than you think. So might the answer.</div>
<div style="height:4mm"></div>
<div class=meta><div><b>FORMAT</b>9:16 · 1080 × 1920</div><div><b>LENGTH</b>36 to 40 seconds</div><div><b>VOICE</b>Warm British narrator</div><div><b>CALL TO ACTION</b>Start your enquiry</div></div>
<h2>What we took from your references</h2>
<div class=refs>
<div><b>"Impossible to miss" (street + interface)</b>Real streets with interface overlays: a search bar typing, a map pin crashing into the street, review stars, a counter climbing, cards like "popular times", a dark end card that types the line and a search bar with the URL.</div>
<div><b>Swipe-app cards</b>Familiar app language used to tell a story: cards that pop, a tick or a cross, a cursor that taps the button at the end.</div>
<div><b>BMHC Wrapped</b>Counters that roll, words that land on the beat, a different transition on every cut, 3D objects that pop and float, a circle wipe into the end card.</div></div>
<h2>Why this works now</h2>
<p><b>FOOH (fake out-of-home)</b>, CGI objects dropped into real places, remains one of the most shared ad formats, from Maybelline's pioneering clip to the 2026 FOOH awards. Industry voices also warn about trust, so this reel keeps it gentle and clearly playful: the giant pin and the paper aeroplane are obviously illustrative, and every fact on screen is sourced. Interface overlays (search, cards, counters) read instantly on a phone and give each beat a clear job.</p>
<h2>The idea</h2>
<p>People search for everything near them. The reel starts with a search for "foster carer near me" and turns it round: what if the answer is you? A giant Organic Fostering pin drops into a real Greater Manchester scene. Cards answer "Could I do this?" the honest way: you do not need all the answers. Then the matching promise, the real UK need, the support, and one call to action.</p>
<h2>Full voiceover <span style="font-weight:400;color:#655563;font-size:10pt">(calm, plain and kind; about 34 seconds of speech)</span></h2>
<div class=vofull>{vo_full}</div>
<h2 class=pb>Beat by beat</h2>
{rows}
<h2>Brand checks</h2>
<ul class=small>
<li>Tone: "you" and "we"; short sentences; sentence case; no exclamation marks; no em dashes; says what happens next and that it carries no obligation; "Start your enquiry" is the only call to action.</li>
<li>Words from the guide: "children in care", "safe home", "allowances" (never earn or salary), "a home for as long as needed" (never forever home), no "rescue" language.</li>
<li>Facts used: Rated Good by Ofsted (May 2025), cultural matching, training and advice outside normal hours, published allowances, 0161 241 1332 (all from the brand guide); 6,000 more foster families needed across the UK in the next 12 months (The Fostering Network, 2026).</li>
<li>Photography: the brand's own campaign images (shared activity, golden hour, light grain). No children alone, crying or at windows; no real children in care. 3D objects are illustrative.</li>
<li>Type and colour: Nunito 800 display with tight tracking, 400 body; plum, magenta, orange, green on ivory; full-colour logo on the light end card; three-colour bar sign-off; leaf pattern; rounded corners on cards.</li>
</ul>
<h2>Caption</h2>
<div class=cap>Somewhere near you, a child needs a safe place to land. You do not need to arrive with all the answers. A spare room, time and patience are a good start, and we stay alongside you with training, advice outside normal hours and published allowances.<br><br>Thinking about fostering in Greater Manchester? Start your enquiry via the link in our bio. It carries no obligation.<br><br>#OrganicFostering #FosteringManchester #BecomeAFosterCarer #FosterCare</div>
<h2>Sources</h2>
<ul class=small>
<li>Organic Fostering brand guidelines v1.0 (September 2026) and organicfostering.co.uk.</li>
<li>The Fostering Network, Recruitment targets for 2026: thefosteringnetwork.org.uk/for-fostering-services/recruitment-and-retention/fostering-recruitment-targets/</li>
<li>Marketing Brew, Why some brands are embracing fake out-of-home: marketingbrew.com/stories/2023/10/26/why-some-brands-are-embracing-fake-out-of-home</li>
<li>FOOH.com, FOOH trends: fooh.com/blog/fooh-trends-in-2025 · Marketing-Interactive, Are FOOH ads pushing creatives to reimagine their boundaries.</li>
</ul>
</body></html>'''
open(f'{OUT}/content.html', 'w').write(html)
js = f"""const {{ chromium }} = require('playwright');
(async () => {{ const b = await chromium.launch(); const p = await b.newPage();
await p.goto('file://{OUT}/content.html'); await p.waitForTimeout(700);
await p.pdf({{ path: '{OUT}/OF_closer_than_you_think_content.pdf', format: 'A4', printBackground: true,
  margin: {{ top: '14mm', bottom: '14mm', left: '14mm', right: '14mm' }} }});
await b.close(); }})();"""
subprocess.run(['node', '-e', js], check=True)
os.remove(f'{OUT}/content.html')
print('pdf written')
