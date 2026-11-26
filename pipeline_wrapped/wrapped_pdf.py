"""PDF: BMHC "Wrapped 2026" reel - concept, scene-by-scene script with frames, transitions, sound, facts to confirm.
-> reel/bmhc/wrapped_2026/BMHC_Wrapped_2026_reel_script.pdf"""
import os, base64, subprocess
import cv2

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ST = f'{ROOT}/workspace_wrapped/stills'
FON = f'{ROOT}/workspace_sol/fonts'
OUT = f'{ROOT}/reel/bmhc/wrapped_2026'
os.makedirs(OUT, exist_ok=True)


def b64file(p, mime):
    return f'data:{mime};base64,' + base64.b64encode(open(p, 'rb').read()).decode()


def frame(ts, w=300):
    im = cv2.imread(f'{ST}/{int(round(ts * 100)):05d}.png')
    im = cv2.resize(im, (w, int(w * 16 / 9)), interpolation=cv2.INTER_AREA)
    ok, b = cv2.imencode('.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 88])
    return 'data:image/jpeg;base64,' + base64.b64encode(b.tobytes()).decode()


def ff(w):
    return f"@font-face{{font-family:Inter;font-weight:{w};src:url({b64file(f'{FON}/Inter-{w}.ttf', 'font/ttf')})}}"


SCENES = [
    (3.3, '0:00 – 0:04', 'Intro · in the reference\'s language', 'Your 2026 at the centre is <b class=m>ready.</b>',
     'Light ground with soft magenta and teal corners. COMMUNITY tag in the first second. A stack of three story cards (magenta, teal, lime) fans in; the front card reads "BMHC Wrapped 2026 · ▶ Play". 3D lantern, rings and radio peek out from behind.',
     'Words rise in; "ready." lands in magenta and a hand-drawn swoosh draws itself under it. Cards slide up and fan with depth shadows; objects pop with overshoot and float. A cursor glides in and taps Play (ripple).',
     'Zoom-through: the Play card grows to fill the screen and becomes the first slide.', 'Soft whoosh, card swishes, a click on Play.'),
    (6.8, '0:04 – 0:08', 'Title slide · magenta', '<b>BMHC</b> / <b>Wrapped</b> / <b>2026</b> · A year at the British Muslim Heritage Centre',
     'Full-screen Heritage Magenta with drifting colour blobs. Story progress bars across the top. Five 3D objects orbit below the title (lantern, ball, Qur\'an stand, rings, map pin).',
     'Each word slams in (scale 135% to 100% with a settle). Objects pop in one after another and orbit slowly in depth.',
     'Story push: the slide is swiped left with motion blur.', 'Three soft hits under the three words; a low whoosh.'),
    (11.5, '0:08 – 0:13', '52 Fridays · teal', 'This year, you showed up. <b>52</b> <b>Fridays.</b> 52 Jummahs at the centre.',
     'Heritage Teal. A giant counter. The 3D lantern glows on the right. White sticker stars spin in.',
     'Counter rolls 0 to 52; "Fridays." slams; the subline rises.', 'Iris: a circle opens from the centre into the next slide.', 'Counter ticks speeding up, a soft bell-like tone at 52.'),
    (16.5, '0:13 – 0:18', 'Most played · orange', 'Most played: <b>Heritage Radio</b> · 90.6 FM · DAB+ · the app · Alexa',
     'Heritage Orange. The 3D retro radio, big. A live equaliser bounces along the bottom.',
     'Radio pops and floats; words slam; equaliser bars animate to the rhythm.', 'Four-bar wipe: magenta, teal, orange and lime bars sweep down the screen in brand order.', 'A dial sweep and a little radio static, then the equaliser\'s soft pulse.'),
    (23.5, '0:18 – 0:25', 'Your top 5 · ink', '<b>Your top 5</b> — 1 Friday Jummah · 2 Qur\'an classes · 3 Youth clubs & taekwondo · 4 Heritage tours & Umrah · 5 Nikah ceremonies',
     'Ink ground. Five charcoal rows, numbers in the four brand colours, each row with its 3D object (lantern, Qur\'an stand, ball, map pin, rings).',
     'Rows slide in from the right one by one (0.75 s apart), each object popping as its row lands.', 'Zoom punch: cut on the beat with a quick zoom.', 'One soft tick per row.'),
    (29.0, '0:25 – 0:30', 'Your year in numbers · lime', '<b>130K+</b> visitors a year · <b>14</b> awards · <b>12+</b> years of Muslim heritage',
     'Heritage Lime with ink type (approved pairing). Three counters stacked. Source line: figures as stated on bmhc.org.uk.',
     'Counters roll up one after another; labels rise.', 'Blur dissolve into a dreamy blur.', 'Counter ticks, three soft hits.'),
    (33.0, '0:30 – 0:34', 'Your aura · mist', 'Your aura: <b>Welcoming</b> · Grounded · Clear · Proud of heritage',
     'Mist ground with four soft colour blobs drifting (the Wrapped "aura" look), the centre\'s online personality from the brand guide.',
     'Blobs drift; "Welcoming" slams; the other three words pop in as chips.', 'Blob morph: the aura blobs swell into the photograph.', 'A soft airy swell.'),
    (37.0, '0:34 – 0:38', '1 tower. 4 seasons.', '<b>1 tower.</b> <b>4 seasons.</b> Whalley Range, Manchester',
     'The building in snow dissolving into the building in autumn, with a warm light leak passing through; a slow push in.',
     'Ken Burns zoom; light-leak dissolve; words slam.', 'Whip up: a vertical whip with motion blur back to the light ground.', 'Wind-like whoosh; quiet room tone.'),
    (39.9, '0:38 – 0:41', 'See you in 2027 · CTA', 'See you in <b class=m>2027.</b> · Share your Wrapped',
     'Back to the reference\'s light ground. A white card with the official logo (background removed), "Your 2026 at the centre", a magenta "Share your Wrapped" button. Ball and lantern float.',
     'Card rises; cursor glides to the button and taps.', 'Circle wipe: a magenta circle grows out of the button and fills the screen.', 'Click, then a rising whoosh.'),
    (42.0, '0:41 – 0:43', 'End card', 'Join us at the centre <b class=m>in Whalley Range</b> · bmhc.org.uk',
     'Official logo large, the line, the website; the four bars wipe in from the left in fixed order (brand signature).',
     'Held still for the last seconds.', '—', 'Soft resolve, room tone to the end.'),
]
TRANS = [(4.0, 'Zoom-through'), (8.5, 'Story push'), (13.5, 'Iris'), (18.5, 'Four-bar wipe'), (25.5, 'Zoom punch'),
         (30.5, 'Blur dissolve'), (34.0, 'Blob morph'), (38.0, 'Whip up'), (40.45, 'Circle wipe')]

rows = ''.join(f'''<div class=scene><img src="{frame(ts)}"><div class=sc>
<div class=hd><span class=tc>{tc}</span><span class=nm>{name}</span></div>
<p class=os>{ons}</p>
<div class=g><span class=k>Visual & 3D</span><span>{vis}</span><span class=k>Animation</span><span>{anim}</span>
<span class=k>Transition out</span><span>{tr}</span><span class=k>Sound</span><span>{snd}</span></div></div></div>''' for ts, tc, name, ons, vis, anim, tr, snd in SCENES)
trs = ''.join(f'<figure><img src="{frame(ts, 220)}"><figcaption>{n}</figcaption></figure>' for ts, n in TRANS)
logo = b64file(f'{ROOT}/workspace_bmhc_posts/bmhc_logo_transparent.png', 'image/png')

html = f'''<!doctype html><html><head><meta charset=utf-8><style>
{ff(400)}{ff(500)}{ff(600)}{ff(700)}{ff(800)}{ff(900)}
@page{{size:A4;margin:14mm 14mm 16mm}}
body{{font-family:Inter;color:#0B0B0B;font-size:9.8pt;margin:0}}
.bars{{display:flex;height:4mm;border-radius:1mm;overflow:hidden;margin:4mm 0 6mm}} .bars i{{flex:1}}
h1{{font-weight:900;font-size:30pt;line-height:1.02;margin:6mm 0 2mm}} h1 b{{color:#E60585}}
.sub{{color:#5C5C5C;font-size:11pt}}
.meta{{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm;margin:6mm 0}}
.meta div{{background:#F6F5F1;border-radius:2.5mm;padding:3mm 3.5mm}} .meta b{{display:block;font-size:8pt;color:#E60585;letter-spacing:.08em}}
h2{{font-weight:900;font-size:15pt;margin:7mm 0 3mm}} h2 small{{color:#5C5C5C;font-weight:500;font-size:10pt}}
p{{line-height:1.5;margin:0 0 2.5mm}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:5mm}}
.box{{background:#F6F5F1;border-radius:3mm;padding:4mm 5mm;line-height:1.5}} .box b.h{{display:block;font-weight:800;margin-bottom:1.5mm}}
.ink{{background:#0B0B0B;color:#fff}} .ink b.h{{color:#69FF00}}
.scene{{display:flex;gap:5mm;padding:4mm 0;border-bottom:1px solid #E9E6DF;break-inside:avoid}}
.scene img{{width:34mm;height:60.4mm;border-radius:2mm;object-fit:cover;box-shadow:0 1mm 3mm rgba(0,0,0,.2)}}
.sc{{flex:1}} .hd{{display:flex;gap:3mm;align-items:center;margin-bottom:1.5mm}}
.tc{{background:#0B0B0B;color:#fff;font-weight:800;border-radius:1.5mm;padding:.5mm 2mm;font-size:8.5pt}}
.nm{{font-weight:800;font-size:11pt}}
.os{{font-size:11pt;margin-bottom:2mm}} .os b{{font-weight:800}} b.m{{color:#E60585}}
.g{{display:grid;grid-template-columns:27mm 1fr;column-gap:2mm;row-gap:1.4mm;line-height:1.42}}
.k{{color:#E60585;font-weight:800;font-size:7.8pt;letter-spacing:.06em;text-transform:uppercase;padding-top:.4mm}}
.trs{{display:grid;grid-template-columns:repeat(5,1fr);gap:3mm}} figure{{margin:0}} figure img{{width:100%;border-radius:2mm}}
figcaption{{font-weight:700;font-size:8.5pt;margin-top:1mm;text-align:center}}
ul{{margin:0;padding-left:5mm}} li{{margin-bottom:1.6mm;line-height:1.45}}
.cap{{background:#F6F5F1;border-left:1.5mm solid #E60585;padding:3.5mm 4.5mm;border-radius:0 2mm 2mm 0;line-height:1.55}}
.pb{{page-break-before:always}}
</style></head><body>
<img src="{logo}" style="width:62mm">
<div class=bars><i style="background:#E60585"></i><i style="background:#2DC892"></i><i style="background:#FF4200"></i><i style="background:#69FF00"></i></div>
<div class=sub>INSTAGRAM REEL · CONCEPT & SCRIPT · NOVEMBER 2026</div>
<h1>BMHC <b>Wrapped</b> 2026</h1>
<div class=sub>A year at the British Muslim Heritage Centre, told in the "Wrapped" format everyone shares in December.</div>
<div class=meta><div><b>FORMAT</b>9:16 · 1080 × 1920</div><div><b>LENGTH</b>43 seconds · 30 fps</div><div><b>SOUND</b>Sound-led (no music)</div><div><b>POST</b>Early December</div></div>
<h2>The idea</h2>
<p>Every December, millions of people share their year-in-review "Wrapped" story cards. BMHC Wrapped turns the centre's year into the same swipeable, colourful format: big numbers, a "most played", a top 5, an "aura" — so it feels native to the feed and invites people to share their own favourite moment at the centre.</p>
<p>It opens and closes in the language of your reference video: a light ground with soft colour corners, a sentence with one accented word, UI cards and a cursor tap. In between, full-screen Wrapped story slides in BMHC's four colours, with glossy 3D objects for each service.</p>
<div class=two>
<div class=box><b class=h>Why it should travel</b>Recaps and rapid-fire round-ups are among the formats Later highlights for Reels this autumn; Wrapped is the most recognisable recap of all and peaks in early December. Story-style slides with progress bars read instantly on a phone, and each slide is a natural screenshot to share.</div>
<div class="box ink"><b class=h>Built to the BMHC brand guide</b>Inter type (ExtraBold for impact words), the four colours as full slides with approved text pairings (white on magenta and ink; ink on teal, orange and lime), COMMUNITY tag in the first second, official logo on the end card, four bars wiping in from the left. No identifiable people; no Qur'an text; sound-led with no music.</div>
</div>
<h2>Motion toolkit <small>— every cut has a purpose</small></h2>
<p>Zoom-through · story push with motion blur · iris · four-bar wipe · zoom punch on the beat · blur dissolve · blob morph · light-leak dissolve · vertical whip · circle wipe. Inside slides: words slam in with a settle, counters roll up, rows slide in, 3D objects pop with overshoot and float, an equaliser bounces, blobs drift, a cursor taps with a ripple, and the camera pushes slowly on the photograph.</p>
<h2 class=pb>Scene by scene</h2>
{rows}
<h2 class=pb>The transitions</h2>
<div class=trs>{trs}</div>
<h2>Sound</h2>
<p>Sound-led, following the brand guide's default of no music: soft UI sounds (card swishes, a click on Play and on Share), three gentle hits under the title words, counter ticks, a radio dial sweep and a breath of static on "Most played", one tick per top-5 row, an airy swell for the aura, wind under the snow-to-autumn dissolve, room tone under the end card. Mastered to −14 LUFS. Optional: a short narrator line on the first and last slides ("Your 2026 at the centre is ready." / "See you in 2027.") — ElevenLabs credits reset around 29 November, or a free British neural voice now.</p>
<h2>Facts to confirm with BMHC before posting</h2>
<ul>
<li><b>Top 5 order</b> (Jummah, Qur'an classes, youth clubs & taekwondo, heritage tours & Umrah, Nikah) — swap in BMHC's own ranking if they have one, or call it "Five things you came for".</li>
<li><b>52 Fridays / 52 Jummahs</b> — 2026 has 52 Fridays; confirm Jummah was held every week.</li>
<li><b>130K+ visitors a year, 14 awards, 12+ years</b> — as stated on bmhc.org.uk; confirm they are current.</li>
<li><b>Heritage Radio</b> — 90.6 FM, DAB+ Manchester, the Heritage Radio app, Alexa (as on the Heritage Radio page).</li>
<li>If BMHC has real 2026 numbers (classes run, Nikahs, radio hours, volunteers), any slide can take them instead.</li>
</ul>
<h2>Caption</h2>
<div class=cap>Your 2026 at the centre, wrapped. 52 Fridays, Heritage Radio on 90.6 FM, and a top 5 only this community could make. What was your favourite moment at BMHC this year? Tell us below. 📍 College Road, Whalley Range · bmhc.org.uk<br><br>#BritishMuslimHeritage #Manchester #WhalleyRange #BMHCWrapped</div>
<h2>Next step</h2>
<p>Approve the scenes (or send changes) and the 43-second video is rendered with all transitions, animation and sound — about 15 minutes.</p>
</body></html>'''
open(f'{OUT}/wrapped.html', 'w').write(html)
js = f"""const {{ chromium }} = require('playwright');
(async () => {{ const b = await chromium.launch(); const p = await b.newPage();
await p.goto('file://{OUT}/wrapped.html'); await p.waitForTimeout(700);
await p.pdf({{ path: '{OUT}/BMHC_Wrapped_2026_reel_script.pdf', format: 'A4', printBackground: true,
  margin: {{ top: '14mm', bottom: '16mm', left: '14mm', right: '14mm' }} }});
await b.close(); }})();"""
subprocess.run(['node', '-e', js], check=True)
os.remove(f'{OUT}/wrapped.html')
print('pdf written')
