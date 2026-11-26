"""PDF for the OF carousel "A safe place to land": concept, the seamless strip, slide-by-slide copy + motion, caption,
posting notes. -> reel/organic_fostering/safe_place_to_land/OF_safe_place_to_land_carousel.pdf"""
import os, base64, subprocess
import cv2

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
D = f'{ROOT}/reel/organic_fostering/safe_place_to_land'
FON = f'{ROOT}/workspace_sol/fonts'


def b64(p, mime):
    return f'data:{mime};base64,' + base64.b64encode(open(p, 'rb').read()).decode()


def jpg(path, w):
    im = cv2.imread(path)
    im = cv2.resize(im, (w, int(im.shape[0] * w / im.shape[1])), interpolation=cv2.INTER_AREA)
    ok, b = cv2.imencode('.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 88])
    return 'data:image/jpeg;base64,' + base64.b64encode(b.tobytes()).decode()


def ff(w):
    return f"@font-face{{font-family:Nunito;font-weight:{w};src:url({b64(f'{FON}/Nunito-{w}.ttf', 'font/ttf')})}}"


SLIDES = [
    ('EVERY CHILD NEEDS A', 'SAFE PLACE TO LAND.', 'Foster carers make the landing soft.',
     'A child\'s orange paper aeroplane takes off; its plum trail starts here and runs off the right edge.',
     'The plane lifts off and flies to the edge; the trail draws itself behind it.'),
    ('SOME JOURNEYS HAVE', 'A FEW LOOPS.', 'New homes. New schools. New faces.',
     'The trail swings into a big loop — the moves and changes many children in care go through.',
     'The plane enters from the left, flies the full loop, and leaves on the right.'),
    ('ALONG THE WAY,', 'SMALL THINGS MATTER.', 'A bedtime story. A drawing. A seat at the table.',
     'The trail waves past small 3D things: an open book, a heart, a crayon, a star.',
     'Each object pops up with a little bounce as the plane passes it, then floats.'),
    ('YOU COULD BE THE', 'SOFT LANDING.', 'Foster with Organic Fostering in Greater Manchester.',
     'The trail glides down and runs in behind a 3D house; the plane comes in to land beside it.',
     'The plane descends to the house; a warm glow lights up behind it as it lands.'),
    ('THINKING ABOUT FOSTERING IN', 'GREATER MANCHESTER?', 'organicfostering.co.uk',
     'The official logo on top; the trail ends at the plum "Start your enquiry" button.',
     'The trail draws in to the button, which gives a gentle pulse.'),
]

rows = ''.join(f'''<div class=slide><img src="{jpg(f'{D}/slide_{i + 1}.jpg', 420)}"><div>
<div class=n>SLIDE {i + 1}</div><div class=hl><span>{a}</span><b>{b}</b></div><div class=sub>{c}</div>
<div class=g><span class=k>Visual</span><span>{v}</span><span class=k>Motion (video slide)</span><span>{m}</span></div></div></div>'''
               for i, (a, b, c, v, m) in enumerate(SLIDES))
logo = b64(f'{ROOT}/workspace_three/web/logo.png', 'image/png')
strip = jpg(f'{D}/carousel_strip.jpg', 1600)

html = f'''<!doctype html><html><head><meta charset=utf-8><style>
{ff(400)}{ff(700)}{ff(800)}{ff(900)}
@page{{size:A4;margin:14mm}}
body{{font-family:Nunito;color:#2B2B2B;font-size:10pt;margin:0}}
h1{{font-weight:900;color:#5B174F;font-size:28pt;margin:4mm 0 1mm;line-height:1.05}}
.sub0{{color:#7a6a75;font-size:11pt}}
.bar{{height:3mm;border-radius:2mm;margin:5mm 0;background:linear-gradient(90deg,#5B174F 0 25%,#B7006E 25% 50%,#FF6411 50% 75%,#61A80A 75%)}}
.meta{{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm;margin-bottom:5mm}}
.meta div{{background:#FCF8F5;border:1px solid #EADFE6;border-radius:3mm;padding:3mm}} .meta b{{display:block;color:#B7006E;font-size:8pt;letter-spacing:.06em}}
h2{{color:#5B174F;font-weight:900;font-size:14pt;margin:6mm 0 3mm}}
p{{line-height:1.5;margin:0 0 2.5mm}}
.strip{{width:100%;border-radius:2mm;box-shadow:0 1mm 3mm rgba(91,23,79,.2)}}
.slide{{display:grid;grid-template-columns:58mm 1fr;gap:6mm;padding:4mm 0;border-bottom:1px solid #EADFE6;break-inside:avoid}}
.slide img{{width:58mm;border-radius:2mm;box-shadow:0 1mm 3mm rgba(0,0,0,.15)}}
.n{{font-weight:800;color:#B7006E;font-size:8.5pt;letter-spacing:.1em}}
.hl{{margin:1.5mm 0}} .hl span{{display:block;font-size:11pt;letter-spacing:.04em}} .hl b{{display:block;color:#5B174F;font-weight:900;font-size:15pt}}
.sub{{font-weight:700;margin-bottom:3mm}}
.g{{display:grid;grid-template-columns:34mm 1fr;column-gap:2mm;row-gap:1.6mm;line-height:1.45}}
.k{{color:#B7006E;font-weight:800;font-size:8pt;text-transform:uppercase;letter-spacing:.05em}}
.cap{{background:#FCF8F5;border-left:1.5mm solid #5B174F;padding:3.5mm 4.5mm;border-radius:0 2mm 2mm 0;line-height:1.55}}
ul{{margin:0;padding-left:5mm}} li{{margin-bottom:1.6mm;line-height:1.45}}
.pb{{page-break-before:always}}
</style></head><body>
<img src="{logo}" style="width:55mm">
<div class=bar></div>
<div class=sub0>INSTAGRAM CAROUSEL · SEAMLESS · 5 SLIDES · WITH MOVING OBJECT</div>
<h1>A safe place to land</h1>
<div class=sub0>One paper aeroplane, one unbroken trail, five slides — from take-off to a home.</div>
<div style="height:5mm"></div>
<div class=meta><div><b>FORMAT</b>4:5 · 1080 × 1350</div><div><b>SLIDES</b>5, seamless</div><div><b>VERSIONS</b>Static JPG + 5 s video slides</div><div><b>BRAND</b>Nunito · OF colours</div></div>
<h2>The idea</h2>
<p>After your Pinterest reference: a clean light ground, one bold path running continuously across every slide, a 3D object travelling along it, and minimal type — light capitals with one bold phrase on top and a short line underneath.</p>
<p>For Organic Fostering the object is a child's paper aeroplane in OF orange. Its trail is a thick plum line: it takes off, loops (the moves and changes), passes the small things that make a home (a bedtime story, a drawing, a seat at the table), and lands at a house — "You could be the soft landing". The trail ends at "Start your enquiry". Because the path is drawn once across a 5400-pixel panorama and then cut into slides, every swipe lines up perfectly.</p>
<img class=strip src="{strip}">
<h2 class=pb>Slide by slide</h2>
{rows}
<h2>Caption</h2>
<div class=cap>Every child needs a safe place to land. Some journeys have a few loops — new homes, new schools, new faces. Along the way, the small things matter most: a bedtime story, a drawing on the fridge, a seat at the table. You could be the soft landing.<br><br>Thinking about fostering in Greater Manchester? Start your enquiry via the link in our bio.<br><br>#OrganicFostering #FosteringManchester #BecomeAFosterCarer</div>
<h2>Posting notes</h2>
<ul>
<li><b>Static carousel:</b> upload slide_1.jpg to slide_5.jpg in order — the path joins up as people swipe.</li>
<li><b>Moving version:</b> upload slide_1.mp4 to slide_5.mp4 (5 s each) as a carousel; each slide plays the plane flying its part of the trail. You can also mix: video for slide 1, images for the rest.</li>
<li><b>swipe_preview.mp4</b> shows the whole journey in one go (23 s) — useful as a Reel or Story teaser.</li>
<li>Alt text: "An orange paper aeroplane flies along a plum line that loops, passes a book, a heart, a crayon and a star, and lands at a small house. Text: Every child needs a safe place to land. You could be the soft landing. Start your enquiry."</li>
<li>Brand: Nunito; plum, magenta, orange, green and ivory; official logo unmodified; no exclamation marks; "Start your enquiry". 3D objects rendered in Blender; no real children shown.</li>
</ul>
</body></html>'''
open(f'{D}/land.html', 'w').write(html)
js = f"""const {{ chromium }} = require('playwright');
(async () => {{ const b = await chromium.launch(); const p = await b.newPage();
await p.goto('file://{D}/land.html'); await p.waitForTimeout(700);
await p.pdf({{ path: '{D}/OF_safe_place_to_land_carousel.pdf', format: 'A4', printBackground: true,
  margin: {{ top: '14mm', bottom: '14mm', left: '14mm', right: '14mm' }} }});
await b.close(); }})();"""
subprocess.run(['node', '-e', js], check=True)
os.remove(f'{D}/land.html')
print('pdf written')
