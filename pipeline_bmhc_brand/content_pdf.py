"""Content plan for the BMHC "Brand identity" carousel (after the user's Pinterest reference), before the slides are made.
-> reel/bmhc/brand_identity_carousel/BMHC_brand_identity_carousel_content.pdf"""
import os, base64, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FON = f'{ROOT}/workspace_sol/fonts'
OUT = f'{ROOT}/reel/bmhc/brand_identity_carousel'
os.makedirs(OUT, exist_ok=True)


def b64(p, mime):
    return f'data:{mime};base64,' + base64.b64encode(open(p, 'rb').read()).decode()


def ff(w):
    return f"@font-face{{font-family:Inter;font-weight:{w};src:url({b64(f'{FON}/Inter-{w}.ttf', 'font/ttf')})}}"


SLIDES = [
    ('1', 'Cover', 'Brand / Identity',
     'Big split headline "Brand" + "Identity" over the building in snow (toned), small spec lines: "British Muslim Heritage Centre · Digital & social edition · Whalley Range, Manchester". A row of three post mockups across the middle (the bento post, a Wrapped slide, the ayah card). Logo at the foot. Corner registration marks; header "Visual identity".'),
    ('2', 'Art direction', 'How the feed looks',
     'Collage of real BMHC pieces on a stone ground: the "Everything under one roof" bento post, Wrapped 2026 slides (52 Fridays, Heritage Radio), the ayah card layout, the tower photo. Black tag: ART DIRECTION. Small notes: "Ink, white, one pillar colour, four bars."'),
    ('3', 'Colour', 'Every colour has a job',
     'Four big swatches over a toned photo of the tower, each with its HEX / RGB / CMYK and the theme it carries: Heritage Magenta · Heart Work; Heritage Teal · Qur\'an in Focus; Heritage Orange · Productivity; Heritage Lime · Sunnah daily habits. Neutrals row: Ink, Stone, Mist. Tags: PILLAR COLOURS / NEUTRALS.'),
    ('4', 'Logo', 'One building, two ways',
     'Split slide. Top half ink: PRIMARY LOGO, the full logo reversed. Bottom half white: BUILDING MARK, the tower line art on its own for avatars and watermarks, plus the four bars in fixed order (magenta, teal, orange, lime).'),
    ('5', 'Typography & photography', 'Inter, one family',
     'Spec rows like the reference: SUBHEADLINE · HEADLINE · BODY with a live sample: "ONE VERSE. ONE ACTION." in Inter ExtraBold caps, a sentence-case subhead, a body line. Below: PHOTOGRAPHY tag and a grid of the centre (tower in snow, autumn, the facade, the tower up close). Soft magenta-tint ground.'),
    ('6', 'Call to action', 'Save this',
     '"Now you can read our feed by colour." Big line: "Five themes. One centre." Small: "Magenta for the heart, teal for the Qur\'an, orange for your day, lime for daily habits." Button-style tag: "SAVE THIS POST", then "Follow @thebmhc for weekly reminders". Logo and four bars.'),
]

rows = ''.join(f'<tr><td class=n>{n}</td><td><b>{t}</b><br><span class=h>{h}</span></td><td>{d}</td></tr>' for n, t, h, d in SLIDES)
html = f'''<!doctype html><html><head><meta charset=utf-8><style>
{ff(400)}{ff(500)}{ff(700)}{ff(800)}{ff(900)}
@page{{size:A4;margin:15mm}}
body{{font-family:Inter;color:#0B0B0B;font-size:10pt;margin:0}}
.bars{{display:flex;height:4mm;border-radius:1mm;overflow:hidden;margin:3mm 0 6mm}} .bars i{{flex:1}}
h1{{font-weight:900;font-size:28pt;margin:2mm 0;line-height:1.05}} h1 span{{color:#E60585}}
.k{{font-weight:800;letter-spacing:.14em;font-size:8.5pt;color:#5C5C5C}}
h2{{font-weight:900;font-size:14pt;margin:7mm 0 3mm}}
p{{line-height:1.55;margin:0 0 2.5mm}}
table{{width:100%;border-collapse:collapse}} td{{border-bottom:1px solid #E9E6DF;padding:3mm 2mm;vertical-align:top;line-height:1.45}}
td.n{{font-weight:900;font-size:18pt;color:#E60585;width:10mm}} .h{{color:#5C5C5C}}
.box{{background:#F6F5F1;border-radius:3mm;padding:4mm 5mm;line-height:1.55}}
.ink{{background:#0B0B0B;color:#fff}} .ink b{{color:#69FF00}}
.cap{{background:#F6F5F1;border-left:1.5mm solid #E60585;padding:3.5mm 4.5mm;border-radius:0 2mm 2mm 0;line-height:1.55}}
</style></head><body>
<div class=k>BMHC · INSTAGRAM CAROUSEL · CONTENT PLAN</div>
<h1>Brand <span>Identity</span></h1>
<div class=bars><i style="background:#E60585"></i><i style="background:#2DC892"></i><i style="background:#FF4200"></i><i style="background:#69FF00"></i></div>
<p>A six-slide carousel (4:5, 1080 × 1350) in the style of your reference: an editorial brand-identity case study with grainy coloured grounds, corner registration marks, black label tags, a big split headline, a mockup collage, a palette with colour values, the logos, a type specimen and a call to action.</p>
<p>For BMHC it does a real job for followers: it shows the centre's visual identity and teaches people to read the feed by colour, because every pillar colour stands for a theme. Everything comes from the BMHC Digital &amp; Social Brand Guidelines.</p>
<h2>Slide by slide</h2>
<table>{rows}</table>
<h2>Design system</h2>
<div class="box ink"><b>From the reference:</b> grain texture on every ground · small crosshair marks in the corners · black rectangle labels in tracked capitals · a header line at the top, a wordmark at the foot · big headline type mixed with small spec text · mockups with soft shadows.<br><br>
<b>From the BMHC guide:</b> Inter only (ExtraBold caps for headlines, Medium for labels, Regular for body) · ink, white, stone and mist with one pillar colour leading each slide · the four bars in fixed order · reversed logo on ink, colour logo on white · no identifiable under-18s (building, objects and our own designs only) · no Qur'an text set (the ayah layout is shown with its placeholder).</div>
<h2>Caption</h2>
<div class=cap>Ever wondered why our posts come in different colours? Each one is a theme. Magenta is Heart Work, teal is Qur'an in Focus, orange is Productivity the Islamic Way and lime is Sunnah daily habits. Save this and you will always know what you are about to read. 📍 British Muslim Heritage Centre, Whalley Range<br><br>#BritishMuslimHeritage #Manchester #WhalleyRange #BMHC</div>
<h2>Next</h2>
<p>The six slides are made from this plan (static JPGs) and added to the folder with a strip preview.</p>
</body></html>'''
open(f'{OUT}/content.html', 'w').write(html)
js = f"""const {{ chromium }} = require('playwright');
(async () => {{ const b = await chromium.launch(); const p = await b.newPage();
await p.goto('file://{OUT}/content.html'); await p.waitForTimeout(600);
await p.pdf({{ path: '{OUT}/BMHC_brand_identity_carousel_content.pdf', format: 'A4', printBackground: true,
  margin: {{ top: '15mm', bottom: '15mm', left: '15mm', right: '15mm' }} }});
await b.close(); }})();"""
subprocess.run(['node', '-e', js], check=True)
os.remove(f'{OUT}/content.html')
print('pdf written')
