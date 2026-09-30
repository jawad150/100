# NOVA — Complete Prompt File
### Images (GPT Image 2.5 on OpenArt) → Keyframes → Video (Seedance 2.5 on OpenArt, 4 sequences) · in production order

This file goes with `NOVA-production-bible-v2.md` and `NOVA-visual-storyboard-v2.html`. Shot numbers and timecodes match both.

**How to use this file**
1. Work top to bottom. Every step depends on the one before it.
2. **Everything is generated inside OpenArt:** images with GPT Image 2.5, video with Seedance. Keep every generation, because the Seedance Award verification needs the links.
3. When a step says **LOCK**, save that exact image as an Element under the `@tag` name shown, then stop regenerating it.
4. In the image prompts, `@image1` means "attach the locked image named here as the first reference".
5. The video prompts use your Element tags directly (`@nova`, `@kadeblack` …). If OpenArt limits how many references a clip can take, attach them in the order listed, because the most important one comes first.
6. For Kade, attach **only the wardrobe sheet** for that shot (`@kadeblack` or `@kaderain`), not `@kade` as well. The wardrobe sheet already carries the locked face, and two face references tend to fight each other.
7. **Video = Part C:** four multi-shot sequences in Seedance 2.5 (12s, 24s, 12s, 12s). Part D holds single-shot prompts for repairing any one beat that fails.
8. All lettering (NOVA, the tagline, EAU DE PARFUM) is typed in After Effects, never generated.

---

# PART A — IMAGE SHEETS (GPT Image 2.5)

## A1 · `@nova` — turnaround · 1:1
**Generate 4 variations and pick the best bottle. LOCK as `@nova`. Every other shot depends on this one.**

```
Product photography reference sheet. Six views of the SAME perfume bottle laid
out in two rows of three on a seamless mid-grey sweep.

THE OBJECT — A perfume bottle 13cm tall and 8cm wide, cut from heavy crystal in
deep sapphire blue. The body is a rounded ovoid cut into roughly forty flat
facets, like a brilliant-cut stone scaled up to fit a palm. Through the exact
centre of the ovoid runs a hollow spherical void 3cm across, open front to back,
so light passes straight through and refracts around its inner edge. The crystal
holds a clear luminous blue liquid that reads as lit from within. A brushed
blue-silver metal collar 2cm tall sits at the neck, machined with fine
concentric turning marks. The cap is a solid piece of the same metal cut into
eight radiating spikes of uneven length, like a star burst, the tallest spike
3cm. The flat base carries one small engraved eight-pointed star emblem, shallow.
No other marking anywhere on the object.

THE SIX VIEWS — Top row: straight front with cap on; three-quarter left; full
left side. Bottom row: full right side; three-quarter right; straight-down top
view looking into the star cap. Identical lighting and camera distance in all six.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 1:1. Studio product lighting: one large overhead softbox, two
white side bounces, and a single hard backlight to drive the refraction through
the hollow core. Real glass caustics falling on the sweep beneath. No neon, no
coloured gels, no glow effects, no lens flare, no bloom. No text, no brand name,
no label, no letters or numbers on the bottle or anywhere in frame.
```

## A2 · `@nova` — in-hand and in-context · 4:5
**Attach A1 as @image1. The bottle-being-set-down frame (view 3) is the most important image in the film.**

```
Product-in-context reference sheet, four views in two rows of two.

THE OBJECT — The sapphire crystal perfume bottle from @image1, matching it 100%
in shape, facet count, hollow central void, blue liquid, metal collar and
eight-spike star cap.

THE FOUR VIEWS — 1) Held upright in a man's thin black gloved hand, fingers
wrapped around the faceted body, giving true human scale. 2) Standing alone on
a round black marble plinth top, a single hard light from directly above,
casting a tight real shadow beneath. 3) The same gloved hand setting the bottle
DOWN onto the black marble, the base just touching the stone, fingers about to
release. 4) Mid-spray: the atomizer firing a fine mist onto the inside of a
bare male wrist held just in front of it, the droplets individually resolved,
the nearest sharp and the far ones falling out of focus.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 4:5. Neutral studio light, not blue. Real contact shadows beneath
the object in every view — the bottle has weight and must sit into the surface,
never float. No glow, no bloom, no particle effects. No text, no logo.
```

## A3 · `@nova` — macro details · 4:5 · *(optional; skip if behind)*
**Attach A1 as @image1.**

```
Macro product photography sheet. Six extreme close-up details of the same
sapphire crystal perfume bottle from @image1, matching it 100% in shape, facet
count, colour and proportion. Laid out in two rows of three.

THE SIX DETAILS — 1) The star-burst metal cap from a low angle, showing the
machining marks and one fingerprint smudged across a spike. 2) The brushed metal
collar where it meets the crystal, showing the join seam and a hairline scratch.
3) Light passing through the hollow central void, the refracted inner edge and
the caustic pattern it throws on the surface below. 4) The blue liquid pressed
against the inside of a facet, with one small air bubble caught at the top
shoulder. 5) The engraved eight-pointed star emblem on the base, shallow,
slightly uneven in depth, dust settled in the grooves. 6) The atomizer nozzle
beneath the cap, a fine machined aperture with one dried droplet crusted at
the rim.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 4:5. Shot at 100mm macro, f/8, focus stacked so detail holds edge
to edge. Hard directional light to reveal texture. No glow, no bloom, no lens
flare, no coloured gels. No text, no letters, no numbers, no brand name, no logo.
```

## A4 · `@case` — decoy briefcase · 16:9
**LOCK as `@case`.**

```
Product photography reference sheet. Six views of the SAME briefcase in two
rows of three on a seamless mid-grey sweep.

THE OBJECT — A flat attaché case, 44cm by 32cm by 9cm. The shell is woven
carbon fibre in matte black, the weave pattern catching at an angle. Frame and
corners are anodised aluminium in gunmetal, with one small dent at the front
left corner. Trim and handle are navy calfskin with visible grain and hand
stitching in matching thread. Twin latches in brushed gunmetal. Between the
latches sits a biometric pad with a black glass face. The interior is deep blue
crushed velvet, pristine and unused, milled into one precise cavity in the
exact silhouette of a 13cm faceted ovoid bottle with a star-burst cap — an
ovoid recess with a small spiked recess above it. A thin warm-white LED strip
runs along the inside of the lid at the hinge.

THE SIX VIEWS — Top row: closed front flat; closed three-quarter; closed, lying
flat on wet concrete, seen from low. Bottom row: open flat, cavity EMPTY; open
three-quarter, cavity EMPTY; macro of the latches and biometric pad together.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 16:9. Neutral studio lighting. The LED strip is OFF in all six
views. The biometric pad is dark and inert. The cavity is EMPTY in every open
view — no bottle, no object. No text, no numbers, no brand name, no logo, no
monogram, no serial plate anywhere on the case.
```

## A5 · `@caseempty` — the empty reveal (shot 12 keyframe) · 16:9
**Attach A4 as @image1. LOCK as `@caseempty`.**

```
Product photography, single hero frame. The open briefcase from @image1,
matching 100% in material, proportion, stitching and hardware.

THE FRAME — The case lies open on a dark polished wood table, lid raised to
about 100 degrees, seen from a high three-quarter angle looking down into it.
The blue velvet interior is EMPTY. The precisely milled bottle-shaped cavity —
the ovoid recess and the small star-spiked recess above it — sits perfectly
crisp and clean, the velvet pile untouched and even, as if nothing has ever
been placed in it. Nothing else in the case. The LED strip in the lid is ON,
throwing soft warm-white light down into the empty cavity so its exact shape
reads instantly.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 16:9. A single warm overhead lamp is the key light, everything
else falling into deep shadow — this frame is WARM, not blue. Absolutely no
bottle, no object, and no reflection of a bottle anywhere in frame. No dust
ring, no worn impression, no crushed pile — the velvet is pristine. The empty
bottle shape must read clearly at a single glance. No text, no logo.
```

## A6 · `@kade` — base identity · 16:9
**Step 1: run it 4–6 times and pick ONE face. Step 2: LOCK as `@kade`. That image is `@image1` for A7 and A8.**

```
Character reference contact sheet of one man, six views of the SAME person
laid out in two rows of three on a seamless mid-grey studio backdrop.

THE MAN — 33 years old, South Asian. Height reads 5'11". Lean athletic build,
broad shoulders, narrow waist, long neck. Warm medium-brown skin with an olive
undertone, slightly uneven in tone across the cheeks. Thick black hair, faded
short at the sides, longer on top and pushed back, with one strand fallen
loose over the forehead and a small natural streak of premature grey at the
right temple. Dense straight eyebrows, the left one interrupted by a pale
1cm scar running through it diagonally. Deep-set dark brown eyes with heavy
upper lids, a visible fold, and permanent faint shadow beneath. Straight nose
that deviates very slightly to the right, broken once years ago. Sharp
cheekbones. Defined jawline carrying three days of uneven stubble, denser at
the chin and upper lip than the cheeks. Thin upper lip, fuller lower lip, a
small vertical crease in the centre of the lower lip. Left ear sits marginally
further from the skull than the right. Neutral closed-mouth expression, calm
and entirely unreadable. No smile.

WARDROBE FOR THIS SHEET — Plain black crew-neck cotton t-shirt, no print.

THE SIX VIEWS — Top row: full frontal at eye level; three-quarter turned left
45 degrees; full left profile. Bottom row: full right profile; three-quarter
turned right 45 degrees; head tilted slightly down with eyes lifted to camera.
Identical lighting, identical camera distance, identical expression across all
six. Head and upper chest only.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 16:9. Flat even studio lighting, no coloured light, no rim light,
no drama. Plain backdrop, no background elements, no props. No text anywhere in
frame. No logo. The same person in all six views with zero identity drift.
```

## A7 · `@kadeblack` — vault wardrobe · 16:9
**Attach `@kade` as @image1. LOCK as `@kadeblack`.**

```
Wardrobe reference sheet, three views of the man in @image1 who matches the
reference 100% — same face, same scar through the left eyebrow, same grey
streak at the right temple, same stubble pattern.

WARDROBE — Matte black technical field jacket, short cut, standing collar,
concealed zip, no visible hardware, no pockets on the chest. The jacket cuffs
are loose enough to slide back and bare the left wrist. Black slim technical
trousers with a reinforced panel at the knee. Thin black tactical gloves with
a second-skin fit that stop exactly at the wrist bone, fingertips visibly worn
and slightly shiny. Black low-profile boots with a soft sole, scuffed at the
toe. A slim black nylon harness worn under the open jacket, two empty webbing
loops at the chest. A matte black head-mounted optic with a single lens barrel,
pushed up on the forehead, lens dark and inert. Every surface matte, nothing
reflective anywhere.

THE THREE VIEWS — Full length frontal, gloves on, optic pushed up. Full length
three-quarter right, jacket half open showing the harness beneath. Detail view
from chest to hips: the left jacket cuff pulled back with the right gloved
hand, baring two inches of the left wrist above the glove line.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 16:9. Seamless mid-grey backdrop. Flat even studio lighting.
Face identical to @image1. No coloured light. No text, no logo, no insignia,
no patches, no brand marks, no visible zippers with pulls. No watch — the
bared wrist is bare skin only.
```

## A8 · `@kaderain` — roof and final walk · 16:9
**Attach `@kade` as @image1. LOCK as `@kaderain`.**

```
Wardrobe reference sheet, two full-body views and one close view of the man
in @image1 who matches the reference 100% — same face, same scar through the
left eyebrow, same grey streak at the right temple.

WARDROBE — Long black wool overcoat, unbuttoned, collar turned up, worn over
a plain black crew-neck and black slim trousers, visibly soaked across the
shoulders and darker where the water has landed, the wool showing its nap
where wet. The overcoat is sharp enough to pass unnoticed at a black-tie
gala. Hair wet and pushed back off the forehead, individual strands
separated, water beading at the temples and one drop running down the left
cheek. Skin damp with a natural sheen from water, not from oil. Bare hands,
no gloves. The coat sleeve ends just above the left wrist; bare wrist, no
watch.

THE THREE VIEWS — Full length frontal, coat open, hands loose at the sides.
Full length three-quarter left, caught mid-stride walking, the coat moving
with real weight. Close view from chest to crown showing wet hair, wet skin
and water droplets caught in the stubble.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 16:9. Seamless mid-grey backdrop. Flat even studio lighting only
— the subject is wet, the light is NOT blue. Face identical to @image1. Bare
wrists. No text, no logo.
```

## A9 · `@vero` — base identity · 16:9
**Run it 4–6 times, pick ONE face, and LOCK as `@vero`.**

```
Character reference contact sheet of one woman, six views of the SAME person
in two rows of three on a seamless mid-grey studio backdrop.

THE WOMAN — 31 years old, Mediterranean features. Height reads 5'8". Slim,
long-necked, very straight posture. Light olive skin with a faint natural
flush across the cheekbones. Dark brown hair pulled back into a low twisted
knot at the nape, with a few deliberately loose strands falling at the temples.
Strong straight brows, barely groomed. Grey-green eyes, level and direct, set
slightly wide. High flat cheekbones. Narrow straight nose with a fine bridge.
A small dark mole on the right cheekbone, 1cm below the outer corner of the
eye. Full mouth, neutral and closed, the upper lip slightly asymmetric.
Minimal makeup, matte skin, no gloss, no contour. Expression composed and
faintly cold.

WARDROBE FOR THIS SHEET — Plain black fitted sleeveless top.

THE SIX VIEWS — Top row: frontal at eye level; three-quarter turned left 45
degrees; full left profile showing the knot at the nape. Bottom row: full right
profile; three-quarter turned right 45 degrees; looking back over her left
shoulder toward camera, eyes half-lowered as if catching a scent.
Head and shoulders only, identical lighting and distance in all six.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 16:9. Flat even studio lighting, no coloured light, no rim light.
No earrings, no necklace, no jewellery. No props. No text, no logo. Same person
in all six views with zero identity drift.
```

## A10 · `@verogown` — gala wardrobe · 16:9
**Attach `@vero` as @image1. LOCK as `@verogown`.**

```
Wardrobe reference sheet, three full-body views of the woman in @image1 who
matches the reference 100% — same face, same mole on the right cheekbone,
same low twisted knot.

WARDROBE — Floor-length midnight blue silk-satin gown, bias cut, thin straps,
a low straight back cut to the waist. The fabric falls with real weight and
catches light in long soft highlights along the drape. No embellishment, no
sequins, no beading, no lace. Bare arms. Bare wrists — no watch, no bracelet.
Hair in the same low twisted knot with the same loose strands.

THE THREE VIEWS — Full length frontal, arms at sides. Full length rear showing
the open back and the full fall of the silk to the floor. Full length turning
back over her left shoulder mid-step, the silk swinging with the turn.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 16:9. Seamless mid-grey backdrop. Flat even studio lighting.
Face identical to @image1. Bare wrists. No jewellery of any kind. No text,
no logo.
```

## A11 · `@solen` — the collector · 16:9
**Run it 2–4 times, pick one, and LOCK as `@solen`.**

```
Character reference contact sheet of one man, four views of the SAME person
in a single row on a seamless mid-grey studio backdrop.

THE MAN — 58 years old, Northern European. Heavy-set through the shoulders and
neck, thick-wristed. Pale skin with visible sun damage across the forehead and
the backs of the hands, and broken capillaries at the cheeks. Silver-grey hair,
thinning at the crown, combed flat and slightly damp-looking. Heavy brow ridge.
Small pale blue eyes set deep, with pronounced crow's feet and loose lower lids.
Broad flat nose, broken once and set slightly off centre. Thin straight mouth.
Soft jowls along the jaw. Clean shaven with visible razor irritation along the
throat. Expression patient and entirely without warmth.

WARDROBE — Charcoal three-piece wool suit, waistcoat buttoned, jacket removed.
White shirt, collar open, no tie, sleeves rolled once. A heavy plain gold
signet ring on the right little finger, worn smooth and featureless.

THE FOUR VIEWS — Frontal head and shoulders. Three-quarter turned left. Full
left profile. Waist-up frontal with both hands resting flat on a table edge,
the signet ring clearly visible.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 16:9. Flat even studio lighting, no warm gold light on this
sheet. The signet ring is plain — no crest, no engraving, no initials. No text,
no logo. Same person in all four views.
```

## A12 · `@vault` — vault chamber plate · 16:9
**LOCK as `@vault`.**

```
Empty location plate, no people. A circular vault chamber 9 metres across.
Floor, walls and domed ceiling in honed black marble with fine grey veining,
matte rather than glossy. A single circular aperture at the apex of the dome,
1 metre across, dropping one vertical shaft of cool white light straight down
to the centre of the floor. At that centre, a waist-height cylindrical plinth
of the same black marble, 80cm across, its base meeting a thin machined steel
ring in the floor. Its top surface is EMPTY. The walls fall away into near
darkness beyond the shaft. Fine dust drifting slowly through the beam.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 16:9. Shot at 35mm, f/4, from chest height angled 15 degrees
down across the plinth, plinth dead centre of frame. The plinth top is empty.
No people. No blue light in this plate — the shaft is neutral cool white so it
can be graded later. No text, no engraving, no markings. No bloom and no
god-ray glow beyond what the real dust in the beam produces.
```

## A13 · `@atrium` — gala atrium plate · 16:9
**LOCK as `@atrium`.**

```
Empty location plate, no people. The interior atrium of a private luxury gallery
at night. Floor of black and white marble in large slabs, polished to a
wet-looking shine. Walls of pale stone rising four storeys to a glass roof. Two
tiers of balcony with slim brass railings. Three long chandeliers of clear
crystal, dimmed low and warm. At the centre of the floor, a waist-height
cylindrical plinth of black marble carrying a single empty glass vitrine lit
from within by cool white light. The plinth rises out of a precise circular
opening in the floor, a thin machined steel ring flush with the marble around
its base, clearly engineered to lower the plinth down into the floor. Empty
champagne coupes clustered on a side console.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 16:9. Shot at 24mm, f/5.6, from chest height. The vitrine is EMPTY.
The steel floor ring around the plinth base is visible. No people, no crowd, no
silhouettes. No text, no signage, no engraved names, no brand marks. No lens
flare, no bloom.
```

## A14 · `@corridor` — security corridor plate · 16:9
**LOCK as `@corridor`.**

```
Empty location plate, no people. A sub-level security corridor. Walls and
ceiling in brushed stainless steel panels with visible seams and countersunk
bolts. Floor in dark textured rubber. The corridor runs 20 metres to a single
sealed door of polished steel with a recessed handle and a small black biometric
panel beside it at chest height. Recessed strip lighting in the ceiling coves,
cold white. A thin scatter of dust visible in the air. Small matte black emitter
housings set into the walls at ankle, waist and shoulder height along the full
run, inert.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 16:9. Shot at 28mm, f/5.6, dead centre, one-point perspective
straight down the corridor from standing height. The emitters are OFF — no
visible beams, no lasers, no glow in this plate. No people. No text, no numbers,
no signage, no warning labels, no brand marks.
```

## A15 · `@roof` — rooftop plate · 16:9
**LOCK as `@roof`.**

```
Empty location plate, no people. A flat rooftop at night in heavy rain, forty
storeys up. The surface is wet grey concrete with standing puddles and a low
parapet wall. Steel vent housings and a run of cable along one edge. Beyond the
parapet, a dense high-rise skyline of scattered lit windows, thrown out of
focus. Rain falling hard, visible in streaks against the darkness. A rooftop
access door of grey steel standing half open on the left, dark inside. A long
clear stretch of flat wet concrete between the door and the centre of frame.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 16:9. Shot at 24mm, f/2.8, from waist height so the wet concrete
dominates the lower third of frame. Skyline soft and out of focus behind. No
people. No helicopter. No text, no signage, no numbers, no brand marks. No lens
flare.
```

## A16 · `@goldroom` — Solen's study plate · 16:9
**LOCK as `@goldroom`.**

```
Empty location plate, no people. A small private study behind a gallery. Dark
oak panelling, aged and unpolished, with visible grain. A round table of dark
polished wood at the centre, bare except for one crystal tumbler and a heavy
glass ashtray. Four leather chairs, cracked and worn at the arms. A single brass
pendant lamp hanging low over the table with a warm tungsten bulb, throwing a
hot pool of light across the tabletop and letting the rest of the room fall into
deep shadow. Thick still cigar smoke hanging in the light.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 16:9. Shot at 50mm, f/2, from seated eye height. This plate is
WARM — tungsten around 2800K, no blue anywhere in frame. No people. No text,
no labels on the glass, no brand marks. No bloom.
```

## A17 · `@street` — rain street plate · 16:9
**LOCK as `@street`.**

```
Empty location plate, no people. A narrow city street at night in heavy rain.
Black wet asphalt holding long vertical reflections. Wet granite kerbstones.
Six-storey stone buildings on both sides, dark, most windows unlit. Anonymous
blue-white signage glowing along one wall at first-floor height — shapes and
light only, no readable characters. A steel drain grate running with water.
Thin atmospheric haze catching the light. One black car parked at the kerb, a
generic modern sedan, no badge, no plate, wet and reflecting the blue.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 16:9. Shot at 35mm, f/4, from standing eye height. Real rain with
visible streaks and splash-back off the road surface. No people. No text of any
kind, no readable signage, no numbers, no brand marks, no licence plate. No lens
flare, no bloom, no glow.
```

## A18 · `@kit` · `@mist` · `@caustic` — *(optional; skip if behind, the video prompts describe them in words)*

```
Product photography reference sheet. Six props laid out in two rows of three on
a matte black rubber surface, shot straight down from directly overhead.

THE SIX PROPS — 1) A pair of thin black tactical gloves, palms up, fingertips
worn and slightly shiny. 2) A head-mounted optic, matte black, single lens
barrel, strap coiled beside it, lens dark and inert. 3) A fibre-optic snake
camera: 60cm of flexible black cable with a 4mm lens head, coiled loosely.
4) A matte black emitter housing, 8cm cube, one dark glass face, unpowered.
5) A biometric reader panel prised out of a wall, 12cm square, black glass face,
loose wires trailing from the back. 6) A small black earpiece with a clear
acoustic tube, lying on its side.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 1:1. Flat overhead softbox plus one raking side light to reveal
texture. Every object shows real use — scuffs, dust, fingerprints, worn edges.
Nothing is powered, nothing glows, no indicator lights anywhere. No text, no
serial numbers, no logos, no brand marks.
```

```
Studio light-study plate. Four frames of the light pattern thrown by a faceted
crystal object, in two rows of two, falling on plain surfaces.

THE FOUR FRAMES — 1) The pattern cast on a flat white plaster wall: a bright
irregular star of light with eight uneven radiating arms and a dark void at its
centre, edges breaking into fine caustic threads. 2) The same pattern cast
across honed black marble, much dimmer, catching only where the stone is
polished. 3) The same pattern falling across a man's face at eye level, the
dark centre over the bridge of the nose, the arms wrapping and distorting over
the cheekbones and brow. 4) The same pattern on a dark wall behind a crystal
object, soft and fading at its outer threads.

PHOTOGRAPHY — Shot on a Sony A7R V, 85mm f/1.8 prime at f/5.6, ISO 200,
1/160s. Lit with a 5ft diffused softbox camera-left at 45 degrees plus a
large white bounce camera-right. Unretouched editorial photography, straight
from the raw file with a light neutral grade.

SKIN AND MATERIAL TRUTH — Visible open pores across the nose, cheeks and
forehead. Fine vellus hair along the jaw and the side of the neck. Natural
facial asymmetry, one eye fractionally lower than the other. Faint capillary
flush at the nostrils and ear edges. Slight natural oil sheen on the forehead
and nose bridge. One or two real skin imperfections left in, unretouched.
Stray flyaway hairs catching the rim light. Fabric shows real weave, real
creases, real weight in the drape. Metal shows fingerprints and micro-
scratches. Glass shows real refraction and one honest smudge.

DO NOT PRODUCE — 3D render, CGI, game engine, Unreal, Octane, ArtStation,
plastic or waxy skin, airbrushed pores, beauty-filter smoothing, perfectly
symmetrical face, glowing eyes, HDR halo, over-sharpened edges, illustration,
digital painting, cartoon, anime, text, letters, numbers, watermark, logo,
signature, brand marks.

CONSTRAINTS — 1:1. This is a REAL optical caustic produced by light passing
through cut glass — not a graphic, not a lens flare, not a drawn star, not a
digital overlay, not a light leak. Neutral white light, no colour, to be graded
blue in post. The centre of the pattern is DARK, not bright. No text, no logo.
```

---

# PART B — KEYFRAMES (GPT Image 2.5)

These are exact start frames for the shots that have to match each other. Feed them to Seedance as the **first frame**.

## K1 · Vault keyframe — first frame of shot 06 AND the whole of shot 13 · 16:9
**Attach `@vault` as @image1 and `@nova` as @image2. LOCK as `@k_vault`. Do not change it after that, because shots 06 and 13 both depend on this exact frame.**

```
Cinematic film still, single frame. The circular black marble vault from
@image1, matching it 100% — same dome, same single aperture, same 80cm black
marble plinth dead centre, same steel floor ring. Standing alone at the exact
centre of the plinth top is the sapphire crystal perfume bottle from @image2,
matching it 100% — faceted ovoid, hollow spherical void through its centre,
luminous blue liquid, brushed blue-silver collar, eight-spike star cap.

LIGHT — One vertical shaft of cold light from the dome aperture falls straight
onto the bottle, 7000K, fine dust drifting in the beam at 20% density. The
bottle glows deep sapphire where the light passes through the hollow core and
throws a small star-shaped caustic onto the plinth top beside it. Everything
beyond the shaft falls to near-black navy. Graded blue: deep navy shadows,
electric blue in the glass, platinum highlights on the metal cap.

CAMERA — 35mm, f/4, chest height, angled 15 degrees down across the plinth.
Plinth and bottle dead centre. Locked-off, symmetrical composition. Empty dark
floor space on the left of frame where a person can enter.

Real photographic grain, true optical depth of field, real contact shadow
under the bottle. No people. No text, no letters, no numbers, no logo.
```

## K2 · Hero bottle keyframe — first frame of shot 15 · 16:9 · *(optional)*
**Attach `@nova` as @image1. LOCK as `@k_hero`.**

```
Cinematic product film still, single frame. The sapphire crystal perfume
bottle from @image1, matching it 100%, standing on an invisible black surface
in a pure black void, centred slightly low in frame. A single hard cold light
from behind and above passes through the bottle's hollow spherical core and
throws a large eight-armed star of light with a dark centre onto a matte black
wall 1 metre behind it, the arms breaking into fine caustic threads. The blue
liquid glows from within. A thin cold rim light traces the facets and the
eight star spikes of the cap. Shallow glossy reflection of the base beneath.

Graded deep navy to electric sapphire, 7500K. Shot at 85mm, f/5.6, eye level
to the bottle. Real photographic grain, true optical caustics. Generous empty
black space in the lower third for typography added in post. No text, no
letters, no logo.
```

---

# PART C — SEEDANCE 2.5 SEQUENCES (main method)

Seedance 2.5 can hold up to 30 seconds, so the 42-second film is built from **4 multi-shot sequences** instead of 17 separate clips. Each sequence stays within one world and one small set of references.

| Seq | Film time | Covers shots | Generate | References (in priority order) |
|---|---|---|---|---|
| **S1 Arrival** | 0:00–0:09 | 01, 02, 03 | **12s** | `@atrium` `@verogown` `@nova` `@street` |
| **S2 The Vault** ★ | 0:09–0:24 **+ 0:32–0:34** | 04, 05, 06, 07, 08, 09A, 09B, **13** | **24s** | `@k_vault` `@nova` `@kadeblack` `@case` `@corridor` |
| **S3 Roof → Gold** | 0:24–0:32 | 10, 11, 12 | **12s** | `@solen` `@caseempty` `@kaderain` `@roof` `@goldroom` |
| **S4 Return → End** | 0:34–0:42 | 14A, 14B, 15 | **12s** | `@kaderain` `@verogown` `@atrium` `@nova` |

**Why not two 30-second clips?**
- **Retries:** if one beat fails in a 30-second clip, you pay to regenerate all 30 seconds. With these four, a failure only costs 12–24 seconds.
- **References:** a 30-second clip spanning street, vault, roof and study needs 9 or more references, and identity drifts as the count goes up.
- **Handles:** each sequence is generated slightly longer than it plays, which leaves room to trim in the edit.

**The big win: shot 13 comes free from S2.** In S2, after Kade walks out, the locked camera holds on the bottle alone for 3 seconds. That hold *is* shot 13, cut out and placed after Solen's scene in the edit. It's the same generation and the same locked camera, so the frame matches shot 06 perfectly.

**Generate S2 first**, because it holds the whole twist. Then S3, S4, S1.

**If one beat inside a sequence fails**, don't regenerate the whole sequence. Use that shot's single prompt from **Part D** (for example V09B) and cut it in.

**If OpenArt caps the reference count**, drop references from the end of the list first.

---

## S1 · Arrival · shots 01–03 · generate 12s

```
SCENE CONTEXT
Night in a rain-soaked city. A man in a long black overcoat steps out of a car
into a puddle; a burst of blue perfume mist fills the frame; then a black-tie
gala in a marble atrium, where the NOVA perfume bottle glows in a vitrine and
a woman in a midnight blue gown stops to look at it before the whole plinth
sinks into the floor.

ACTIVE REFERENCES
@atrium: marble gallery atrium, black plinth with a glass vitrine, thin steel
floor ring around the plinth base, crystal chandeliers, 100% matches the
reference.
@verogown: Vero, 31, dark hair in a low twisted knot, small mole on the right
cheekbone, floor-length midnight blue silk gown, 100% matches the reference.
@nova: sapphire crystal perfume bottle inside the vitrine — faceted ovoid,
hollow spherical void through its centre, luminous blue liquid, eight-spike
metal star cap, 100% matches the reference.
@street: narrow wet stone street at night with abstract blue-white wall
signage, 100% matches the reference.

FORMAT MODE
Timed multishot, cuts only at the specified points, the camera does not cut on
its own.

0.0s to 4.0s — STREET. Wide 84°, camera locked 5cm above black wet asphalt, a
puddle with a blue reflection filling the lower third. The rear door of a black
unbadged sedan on the right swings open; one black shoe steps down into the
puddle, a soaked black overcoat hem falls behind it, water splashes in a crown;
both feet walk out of frame left at 4 km/h. Only legs, shoes and coat hem are
ever in frame. Heavy rain rings the puddle.
4.0s HARD CUT
4.0s to 6.5s — MIST. 63°, pure black void; a burst of fine atomized mist fires
toward the lens from bottom centre and the camera pushes into it at 6 km/h;
droplets sharp at the leading edge, hazy behind; by 6.5s the whole frame is a
glowing electric blue-white veil. 48 fps slow motion in this segment only.
6.5s HARD CUT
6.5s to 12.0s — ATRIUM. 63°, chest height, slow push-in at 2 km/h through a
gap in a black-tie crowd. The glowing vitrine with the NOVA bottle is centred.
6.5s to 8.5s Vero walks in from frame left, slows and stops one metre from the
vitrine, eyes fixed on the bottle, head tilting a few degrees. 8.5s to 12.0s
the plinth, vitrine and bottle descend smoothly into the steel floor ring at
0.3 km/h as one heavy mechanical unit, the glow sinking with it; Vero's gaze
follows it down. Guests keep moving and talking around her.
No drift mid-segment.

PERFORMANCE
Vero is composed and still; desire shows only in her eyes and one small
breath through parted lips. Pore-level skin, catch-lights from the vitrine.

PHYSICS
Rain impacts ring the water; the shoe displaces the puddle with weight; the
mist droplets slow with air resistance; the plinth moves on a smooth track;
the silk gown settles with weight as she stops.

LIGHTING
Street: cold blue-white signage spill from frame left at 8500K, deep black
shadows. Mist: one hard 9000K backlight. Atrium: cold 7000K glow from inside
the vitrine lighting the bottle and Vero's face from below-front, warm 3200K
chandelier fill from above.

COLOR GRADE
Navy and black throughout, electric sapphire and cyan in the mist and the
bottle, warm amber only in the chandelier crystals.

AUDIO
Heavy rain, a car door, one splash and a low bass drone; a crisp atomizer
spray and a rising whoosh; then a soft gala murmur and a low hydraulic hum.

STYLE
Photoreal luxury thriller cinema, fine film grain, 24 fps real time except the
mist segment.

POSITIVE LOCKS
The man's face never appears. One bottle, inside the vitrine, descending with
the plinth. Vero matches the reference. The car is unbadged, signage is
abstract light, and no readable text appears anywhere.
```

---

## S2 · The Vault · shots 04–09B + 13 · generate 24s · ★★ THE TWIST
**Attach `@k_vault` as the vault reference.** Don't use it as the first frame here, because this sequence opens on the macros.

```
SCENE CONTEXT
A thief breaks in and reaches a circular black marble vault where the NOVA
perfume bottle stands alone on a plinth in a shaft of light. He opens an empty
briefcase beside it, lifts the bottle into the light, sprays it once on his
bare wrist, sets the bottle BACK on the plinth, closes the empty case and
leaves. The bottle stays.

ACTIVE REFERENCES
@k_vault: the vault wide frame — circular black marble chamber, one dome
aperture dropping a vertical shaft of light onto an 80cm black marble plinth,
the bottle standing at the plinth centre, camera at chest height angled 15
degrees down, 100% matches the reference.
@nova: sapphire crystal perfume bottle — forty facets, hollow spherical void
through its centre, luminous blue liquid, brushed blue-silver collar,
eight-spike metal star cap, small engraved star emblem on the base, 100%
matches the reference.
@kadeblack: Kade, 33, South Asian, pale scar through the left eyebrow, grey
streak at the right temple, three-day stubble, matte black technical jacket,
thin black gloves ending at the wrist bone, matte black single-lens optic,
100% matches the reference.
@case: matte black carbon fibre attaché case, gunmetal corners, navy leather
handle; inside, pristine blue velvet with one EMPTY bottle-shaped cavity, 100%
matches the reference.
@corridor: brushed stainless steel security corridor, one-point perspective,
100% matches the reference.

FORMAT MODE
Timed multishot, cuts only at the specified points, the camera does not cut on
its own. Every return to the vault wide uses the identical locked frame of
@k_vault.

0.0s to 2.4s — MACROS. Three fast extreme close-ups, 0.8s each, handheld:
a black-gloved hand pressing flat on a brushed-steel panel (12°); the matte
black optic swinging down over his right eye, only eye socket and stubble in
frame (18°); a thin black fibre-optic cable sliding under a steel door gap
toward camera at floor level (12°).
2.4s HARD CUT
2.4s to 5.0s — CORRIDOR. 63°, locked-off dead centre, one-point perspective.
Thin blue laser lines cross the corridor floor to ceiling at irregular angles.
Kade, 5 metres away, turned sideways, slides one leg over a low beam, then
leans back as a diagonal beam passes 5cm in front of his face, grazing his
stubble in blue. Perfectly still, one breath.
5.0s HARD CUT
5.0s to 9.0s — VAULT WIDE. 47°, locked-off, the exact @k_vault frame: the
bottle alone on the plinth in the light shaft. Kade walks out of the darkness
from frame left at 3 km/h carrying the closed case, lays it flat on the plinth
top 20cm left of the bottle, unlatches it and lifts the lid away from camera:
the blue velvet interior faces camera, one precise bottle-shaped cavity,
clearly empty. The bottle stands untouched.
9.0s HARD CUT
9.0s to 11.5s — FACE. MCU 29°, locked at eye level. Kade raises the bottle
into the light shaft at chin height; light through the hollow core projects an
eight-armed star with a dark centre across his face, the dark centre on the
bridge of his nose, the arms over cheekbones and brow. First full view of his
face. He holds completely still, eyes on the bottle.
11.5s HARD CUT
11.5s to 13.0s — PRODUCT MACROS. Two extreme close-ups, 0.75s each, 12°: light
sliding across the crystal facets with the blue liquid shifting and one air
bubble rising; the eight-spike metal star cap from low angle, light travelling
along each spike.
13.0s HARD CUT
13.0s to 15.0s — SPRAY. MCU 29°, focus on the wrist. The cap is off; his
gloved right hand holds the bottle 10cm from his left wrist, jacket cuff pulled
back to bare skin. One press: a fine mist cone hits the inside of the bare
wrist, glowing blue in the light. He lifts the wrist toward his face, eyes
closing, one slow breath in.
15.0s HARD CUT
15.0s to 24.0s — VAULT WIDE, the exact @k_vault frame again, 47°, locked-off
tripod for the entire segment. The open empty case lies on the left of the
plinth top. 15.0s to 16.5s Kade lowers the bottle, cap back on, and sets it
down upright at the exact centre of the plinth; the base touches the stone and
his gloved fingers open and lift away. 16.5s to 17.5s nothing moves; the
bottle stands alone in the light. 17.5s to 19.0s he closes the lid of the
empty case, snaps both latches and lifts it by the handle. 19.0s to 20.5s he
walks out of frame left at 3 km/h; the vault walls wash in a slow pulsing deep
red. 20.5s to 21.5s the red fades out and the cold light returns. 21.5s to
24.0s the frame holds: the empty vault, no one in it, the bottle still
standing upright at the plinth centre in its shaft of light, fine dust
drifting down through the beam.
No drift mid-segment.

PERFORMANCE
Kade: total control and calm; slow breath through the nose, relaxed jaw, no
hesitation, an almost reverent stillness when the star lands on his face.
Pore-level skin, stubble catching blue light, living catch-lights.

PHYSICS
Glove leather creases under pressure; the optic swings with inertia; laser
lines stay perfectly straight and pass in front of him; the case has weight,
latches recoil; mist droplets are real, backlit and bead on skin; the bottle
lands with weight and a real contact shadow; dust falls through the beam.

LIGHTING
Corridor: low cold 6000K cove strips with blue laser lines as the key. Vault:
one hard 7000K vertical shaft from the dome onto the plinth, everything outside
it navy black; the star caustic is the key light on his face; red alarm wash
on the walls only, 19.0s to 20.5s.

COLOR GRADE
Deep navy shadows, electric sapphire and cyan in the glass, mist and lasers,
platinum highlights on metal, natural warm skin under blue.

AUDIO
Metal, servo click, cable hiss; silence and breath in the corridor; footsteps
echoing on marble and latch clicks; a big score swell with sub-bass on the
face; one crisp spray and an inhale; the glass "tok" of the bottle on stone,
held silence, latch clicks, footsteps, a low alarm hum that fades to room tone.

STYLE
Photoreal heist cinema, fine film grain, 24 fps real time.

POSITIVE LOCKS
The vault wide frame is identical every time it appears. The bottle ends the
sequence standing upright at the plinth centre, sharp and clearly visible, for
the final 2.5 seconds. The case is empty from start to finish. The star on his
face has eight arms and a dark centre. Kade's face matches the reference:
eyebrow scar, grey temple streak. No text or markings anywhere.
```

---

## S3 · Roof → Gold room · shots 10–12 · generate 12s

```
SCENE CONTEXT
On a rain-soaked rooftop, guards with torches corner the thief; he calmly
slides the closed briefcase across the concrete to their feet and steps back
into the dark. A burst of gold mist. Then in a dark oak study under a brass
lamp, the collector opens the recovered case: it is empty.

ACTIVE REFERENCES
@solen: Solen, 58, heavy-set, silver hair combed flat, pale blue deep-set
eyes, charcoal waistcoat, sleeves rolled, plain gold signet ring on the right
little finger, 100% matches the reference.
@caseempty: the open matte black case, pristine blue velvet with one empty
bottle-shaped cavity lit by the LED in the lid, 100% matches the reference.
@kaderain: Kade, 33, South Asian, long soaked black wool overcoat, wet hair
pushed back, bare hands, 100% matches the reference.
@roof: flat wet concrete rooftop forty storeys up, steel access door on the
left, blurred skyline, 100% matches the reference.
@goldroom: dark oak study, round dark table, brass pendant lamp, cigar smoke,
100% matches the reference.

FORMAT MODE
Timed multishot, cuts only at the specified points, the camera does not cut on
its own.

0.0s to 5.0s — ROOF. 84°, handheld at waist height behind Kade's right
shoulder, looking toward the door. The steel door on the left is flung open;
three guards as pure backlit black silhouettes aim torches at Kade, who stands
6 metres away on the right holding the closed case. 0.0s to 1.0s the beams find
him and he stops. 1.0s to 2.5s he bends and slides the case along the wet
concrete toward them; it skids 5 metres at 8 km/h throwing water and stops at
their feet. 2.5s to 4.0s two guards lunge for it. 4.0s to 5.0s Kade steps
backward out of the beams into the rain and darkness.
5.0s HARD CUT
5.0s to 6.5s — GOLD MIST. 63°, black void, a burst of fine mist fires toward
the lens as the camera pushes in at 6 km/h, filling the frame with glowing
amber-gold. 48 fps slow motion in this segment only.
6.5s HARD CUT
6.5s to 9.5s — CASE. High angle 47°, locked, looking straight down onto the
round oak table. Solen's hands with the signet ring flip both latches and raise
the lid. The interior faces camera: pristine blue velvet, one precise empty
bottle-shaped cavity, nothing else, lit by the lid LED.
9.5s HARD CUT
9.5s to 12.0s — FACE. MCU 29°, locked. Solen looks down into the case under
the hot lamp: eyes fixed, jaw sets, one slow blink, a nostril flares. Complete
stillness.
No drift mid-segment.

PERFORMANCE
Kade: unhurried, upright, hands open after the release. Solen: stillness,
muscle-level anger held behind the eyes; pore-level skin, broken capillaries,
sweat sheen under the lamp.

PHYSICS
Heavy rain streaks and splashes; the case slides with weight, fans water and
slows with friction; the overcoat drips; mist droplets slow in the air; the
case lid lifts with weight; cigar smoke drifts in the lamp light.

LIGHTING
Roof: hard white 6000K torch beams through rain from the door, guards pure
silhouettes, cold blue skyline glow. Study: one hot 2800K tungsten pendant
directly above the table, everything outside its pool in deep shadow.

COLOR GRADE
Roof in black, navy and white beams. Mist and study in old gold, amber and
dark oak; the only blue in the study is the velvet inside the case.

AUDIO
Rain, distant sirens, the case scraping and skidding, the score at its peak;
the score cuts dead into the mist with a low tungsten hum; two latch clicks,
then total silence.

STYLE
Photoreal noir thriller, fine film grain, 24 fps real time except the mist
segment.

POSITIVE LOCKS
Guards are faceless backlit silhouettes. The case is closed on the roof and
empty in the study, velvet pristine, cavity clearly bottle-shaped. Solen
matches the reference. No text anywhere.
```

---

## S4 · Return → End card · shots 14A, 14B, 15 · generate 12s
**Type the end-card text in AE:** *They took the case. He took NOVA.* → **NOVA** · EAU DE PARFUM.

```
SCENE CONTEXT
The gala upstairs is still going as if nothing happened. The thief, in a wet
black overcoat, walks calmly through the crowd; the woman in the midnight blue
gown passes him, stops and turns back as she catches his scent; he tugs his
cuff over his wrist; then the NOVA bottle alone in a black void, throwing a
star of light onto the wall behind it.

ACTIVE REFERENCES
@kaderain: Kade, 33, South Asian, long soaked black wool overcoat, wet hair
pushed back, grey streak at the right temple, bare hands, 100% matches the
reference.
@verogown: Vero, 31, dark hair in a low twisted knot, mole on the right
cheekbone, floor-length midnight blue silk gown, 100% matches the reference.
@atrium: marble gallery atrium with crystal chandeliers and brass balconies,
100% matches the reference.
@nova: sapphire crystal perfume bottle — forty facets, hollow spherical void,
luminous blue liquid, brushed blue-silver collar, eight-spike metal star cap,
100% matches the reference.

FORMAT MODE
Timed multishot, cuts only at the specified points, the camera does not cut on
its own.

0.0s to 5.0s — WALK. 47°, steadicam 2 metres behind Kade at chest height,
following at 3 km/h through a black-tie crowd toward the far doors, water
dripping from his coat hem. 1.5s to 2.5s Vero, walking toward camera on the
right, passes him shoulder to shoulder. 2.5s to 5.0s she takes two more steps,
slows, stops, and turns her head and shoulders back over her left shoulder
toward him, eyes half closing, lips slightly parted. Kade keeps walking without
looking back.
5.0s HARD CUT
5.0s to 6.5s — CUFF INSERT. ECU 18°, handheld tracking alongside at 3 km/h.
His bare left wrist at hip height mid-walk; a faint cool blue shimmer catches
on the inside of the wrist under the light, then his right fingers tug the wet
overcoat cuff down over it.
6.5s HARD CUT
6.5s to 12.0s — HERO. 29°, a very slow orbit left to right at 0.5 km/h around
the NOVA bottle standing on a glossy black surface in a pure black void,
centred slightly low with empty black space in the lower third. One hard cold
backlight passes through the hollow core and throws an eight-armed star with a
dark centre onto a matte black wall 1 metre behind it. 6.5s to 9.5s the facets
catch the light as the orbit moves. 9.5s to 12.0s the backlight dims slowly and
the star fades to darkness, leaving the bottle glowing faintly blue.
No drift mid-segment.

PERFORMANCE
Vero: a small intake of breath through the nose, eyelids lowering, the
faintest recognition at the corner of her mouth. Kade: completely neutral and
unhurried. Pore-level skin, living catch-lights from the chandeliers.

PHYSICS
Wet wool swings heavily and drips; the silk gown twists with her turn and
settles with weight; the star is a real optical caustic with fine threads;
glossy reflection under the bottle base.

LIGHTING
Atrium: warm 3200K chandelier light from above, cool 7000K spill near the empty
plinth ring, damp highlights on Kade's hair and coat, a thin cool glint on the
wrist. Hero: one hard 7500K backlight through the bottle core, a thin rim on
the cap spikes, black void.

COLOR GRADE
Black crowd, midnight blue silk, amber chandelier accents, navy shadows; the
hero shot in deep navy to electric sapphire with platinum metal.

AUDIO
The gala murmur distant and softened, a single soft sustained note; the final
note, one crisp spray sound, then black silence.

STYLE
Photoreal luxury cinema, fine film grain, 24 fps real time.

POSITIVE LOCKS
Kade and Vero both match their references. Kade keeps walking away; Vero ends
her segment turned back toward him. The wrist is bare skin with only a subtle
blue shimmer. The bottle matches the reference exactly. No text anywhere in the
image.
```

---

## Edit assembly for the 4 sequences

| Film time | Take from | Sequence time | Shot |
|---|---|---|---|
| 0:00–0:03 | S1 | 0.5–3.5 | 01 street |
| 0:03–0:05 | S1 | 4.3–6.3 | 02 blue mist (cut out at the whiteout) |
| 0:05–0:09 | S1 | 7.5–11.5 | 03 Vero + plinth sinks |
| 0:09–0:11 | S2 | 0.2–2.2 | 04 macros |
| 0:11–0:13 | S2 | 2.8–4.8 | 05 corridor |
| 0:13–0:16 | S2 | 6.0–9.0 | 06 empty case opens |
| 0:16–0:18 | S2 | 9.3–11.3 | 07 star on face |
| 0:18–0:20 | S2 | 11.5–13.0 (+ stretch) | 08 product macros |
| 0:20–0:21.5 | S2 | 13.3–14.8 | 09A spray |
| 0:21.5–0:24 | S2 | 15.0–17.5 | **09B bottle set back, hold** |
| 0:24–0:28 | S3 | 0.5–4.5 | 10 roof, case slide |
| 0:28–0:29 | S3 | 5.3–6.3 | 11 gold mist |
| 0:29–0:32 | S3 | 6.5–9.5 | 12 empty case (silence) |
| 0:32–0:34 | **S2** | **21.8–23.8** | **13 bottle still there** (same locked frame as 06) |
| 0:34–0:37 | S4 | 1.5–4.5 | 14A Vero turns |
| 0:37–0:38 | S4 | 5.2–6.2 | 14B cuff |
| 0:38–0:42 | S4 | 7.5–11.5 | 15 hero + AE text |

These in/out points assume Seedance keeps to the timecodes. It will drift a little, so trim by eye and keep the durations in the Film time column.

---

# PART D — SINGLE-SHOT PROMPTS (fallback / repair)

Use these only to **replace one beat that failed inside a sequence** from Part C. Each one also works as a standalone 5s clip.

**Order of generation (hardest first):** 06 → 09B → 13 → 07 → 10 → 12 → 14A/14B → then 01, 02, 03, 04, 05, 08, 09A, 11, 15.
They are **listed below in film order** so the edit is easy to follow.

Every prompt is self-contained, so paste the whole code block. Budget 2–4 attempts per shot.

---

## V01 · 0:00–0:03 · Street arrival · generate 5s
**Refs:** `@street`, `@kaderain`

```
SCENE CONTEXT
Night, heavy rain, an empty city street. A black car door opens at the kerb
and a man's shoe steps down into a rain puddle. His face is never seen.

ACTIVE REFERENCES
@street: the narrow wet stone street with the anonymous blue-white wall
signage, 100% matches the reference.
@kaderain: the man, seen only from the knee down — black slim trousers, black
low-profile shoe, hem of a long soaked black wool overcoat, 100% matches the
reference.

LOCATION MAP
Foreground: black wet asphalt at lens height with a wide puddle holding a blue
reflection. Midground: the rear door of a black unbadged sedan at the kerb,
frame right. Background: dark stone facades, blue-white signage glow on the
left wall, rain streaks against it.

FIRST FRAME / BLOCKING
Camera sits on the road surface, the puddle fills the lower third, the car
door already beginning to swing open on the right.

FORMAT MODE
One continuous shot, the camera does not cut on its own.

OPTICS
Wide, 84° field of view, rectilinear, deep focus with the puddle surface sharp.

CAMERA
Locked-off at 5cm above the asphalt, looking along the street. Rich shadow
latitude, soft highlight roll-off on the wet reflections.

ACTION
0.0s to 1.5s — the car door swings fully open. 1.5s to 3.5s — one black shoe
steps down into the puddle, the hem of the long black overcoat falls into
frame behind it, water splashes outward in a crown. 3.5s to 5.0s — the
second foot follows and both walk out of frame left at walking pace 4 km/h.

PHYSICS
Real rain impacts ring the puddle surface. The shoe displaces water with
weight; droplets arc and fall back. The overcoat hem is heavy and wet.

LIGHTING
Cold blue-white signage spill from frame left at 8500K, a faint warm sodium
edge from far background, deep black shadows everywhere else. Rain streaks
backlit.

AUDIO
Heavy rain, the car door opening, one splash, a low bass drone rising.

STYLE
Photoreal cinematic night exterior, fine film grain, anamorphic-feel
reflections, 24 fps real time.

POSITIVE LOCKS
Only the man's legs, shoes and coat hem are in frame for the entire shot. The
car is unbadged with a blank rear. All signage is abstract light shapes.
```

---

## V02 · 0:03–0:05 · Mist transition (blue) · generate 5s
**Refs:** none (optionally `@mist`). **Edit trick:** cut the end of V01 into the moment this mist fills the frame, then cut out of the white-blue peak straight into V03. That gives you a push "through the spray" without having to generate the transition itself.

```
SCENE CONTEXT
Extreme close studio shot: a single burst of fine perfume mist fires straight
toward the lens and fills the whole frame.

LOCATION MAP
Pure matte black void. The atomizer nozzle sits just out of frame at the
bottom centre. One hard backlight behind the plume.

FIRST FRAME / BLOCKING
Black frame with a tight cone of mist just beginning at the bottom centre.

FORMAT MODE
One continuous shot, the camera does not cut on its own.

OPTICS
Close, 63° field of view, focus on the leading edge of the plume.

CAMERA
Camera pushes forward into the plume at 6 km/h, straight on.

ACTION
0.0s to 1.0s — the mist fires and opens into a cone. 1.0s to 3.0s — the plume
expands toward the lens as the camera pushes in; individual droplets resolve
sharp at the front edge and dissolve into haze behind. 3.0s to 5.0s — the
mist fills the entire frame edge to edge, a luminous blue-white veil.

PHYSICS
Real atomized water droplets, each lit from behind, drifting and slowing with
air resistance, the finest droplets hanging in the air.

LIGHTING
One hard cold backlight at 9000K, droplets glowing electric blue and cyan
against black.

COLOR GRADE
Electric sapphire blue in the lit droplets, cyan flare at the densest part of
the plume, black everywhere else.

AUDIO
One sharp atomizer spray, then a rising airy whoosh.

STYLE
High-speed macro photography look, photoreal, crisp droplets, 48 fps slow
motion for the whole shot.

POSITIVE LOCKS
Only mist and black in frame, the frame ends fully filled with glowing blue
mist.
```

---

## V03 · 0:05–0:09 · The gala, NOVA, Vero, plinth sinks · generate 5s
**Refs:** `@atrium`, `@nova`, `@verogown`

```
SCENE CONTEXT
A black-tie gala in a marble gallery atrium at night. At the centre, the NOVA
perfume bottle glows inside a glass vitrine on a black marble plinth. A woman
in a midnight blue gown stops to look at it. Then the whole plinth sinks
smoothly down into the floor.

ACTIVE REFERENCES
@atrium: the marble atrium with the black plinth, the glass vitrine and the
steel floor ring around the plinth base, 100% matches the reference.
@nova: the sapphire crystal bottle inside the vitrine — faceted ovoid, hollow
spherical void through the centre, luminous blue liquid, eight-spike metal
star cap, 100% matches the reference.
@verogown: Vero, 31, dark hair in a low twisted knot, small mole on the right
cheekbone, floor-length midnight blue silk gown, 100% matches the reference.

LOCATION MAP
Foreground: out-of-focus shoulders of guests in black passing across frame.
Midground: the plinth and glowing vitrine at centre; Vero enters from frame
left and stops one metre from it, facing it, three-quarter to camera.
Background: pale stone walls, brass balcony railings, three dimmed crystal
chandeliers.

FIRST FRAME / BLOCKING
Wide view through a gap in the crowd, the glowing vitrine centred, guests in
motion from frame one, Vero stepping into the left third.

FORMAT MODE
One continuous shot, the camera does not cut on its own.

OPTICS
Wide 63° field of view, rectilinear, focus on the vitrine and Vero.

CAMERA
Slow push-in at 2 km/h from chest height through the crowd gap. Soft
highlight roll-off on the chandeliers.

ACTION
0.0s to 2.0s — Vero walks in from frame left, slows and stops, her eyes fixed
on the bottle. 2.0s to 2.5s — she tilts her head a few degrees, lips part
slightly. 2.5s to 5.0s — the plinth, vitrine and bottle descend smoothly and
steadily into the steel floor ring at 0.3 km/h, the glow sinking with it,
until the top of the vitrine is level with the floor. Vero's gaze follows it
down. Guests keep moving and talking around her.

PERFORMANCE
Vero is composed and still; only her eyes and a small breath show desire.
Skin with natural pores, soft catch-lights in her eyes from the vitrine.

PHYSICS
The plinth moves as one heavy mechanical unit on a smooth track, no wobble.
Silk gown settles with weight as she stops.

LIGHTING
Cold 7000K glow from inside the vitrine lights the bottle and Vero's face from
below-front; warm 3200K chandelier fill from above; deep shadows between
guests.

COLOR GRADE
Navy and black in the crowd, electric sapphire at the vitrine, warm amber
only in the chandelier crystals.

AUDIO
Low gala murmur, glasses, a soft hydraulic hum as the plinth descends.

STYLE
Photoreal luxury cinema, fine grain, 24 fps real time.

POSITIVE LOCKS
One bottle, inside the vitrine, descending with the plinth. Vero's face
matches the reference throughout. All guests wear black; no readable text
anywhere.
```

---

## V04 · 0:09–0:11 · Macro cuts: glove, optic, fibre cam · generate 5s
**Refs:** `@kadeblack`, `@kit` (optional)

```
SCENE CONTEXT
Three fast extreme close-ups of a thief at work in a dark steel service
passage. His face is never shown.

ACTIVE REFERENCES
@kadeblack: the man's matte black tactical gloves, black technical jacket
sleeve and matte black head-mounted single-lens optic, 100% matches the
reference.

FORMAT MODE
Timed multishot, cuts only at the specified points, the camera does not cut on
its own.

0.0s to 1.6s — ECU, 12° field of view, a black-gloved hand presses flat
against a cold brushed-steel panel, fingers spreading, a faint breath of
condensation around the fingertips.
1.6s HARD CUT
1.6s to 3.3s — ECU, 18° field of view, the matte black optic swings down on
its hinge over his right eye, only the eye socket edge, stubble on the cheek
and the optic in frame.
3.3s HARD CUT
3.3s to 5.0s — ECU, 12° field of view, low at floor level, a thin black
fibre-optic cable with a tiny lens head slides under a steel door gap toward
camera.
No drift mid-segment.

CAMERA
Handheld, tight, small natural tremor, focus locked on the action detail.

PHYSICS
The glove leather creases under pressure. The optic swings with inertia and
stops with a small bounce. The fibre cable flexes as it slides.

LIGHTING
Cold 6500K strip light raking from above, hard specular edges on steel and
glove fingertips, everything else in deep shadow.

COLOR GRADE
Gunmetal and black, a thin cyan edge on the metal.

AUDIO
Metal contact, a servo click, a cable hiss. Rain distant and muffled.

STYLE
Photoreal macro cinematography, fine grain, 24 fps real time.

POSITIVE LOCKS
Every segment shows only hands, gear or the eye area. The optic lens stays
dark and inert. No text or markings on any surface.
```

---

## V05 · 0:11–0:13 · Laser corridor · generate 5s

**Refs:** `@corridor`, `@kadeblack`

```
SCENE CONTEXT
A sub-level steel security corridor crossed by thin blue laser lines. A thief
in black moves slowly between them. One beam passes inches in front of his
face.

ACTIVE REFERENCES
@corridor: the brushed stainless steel corridor with the sealed door at the
far end, 100% matches the reference.
@kadeblack: Kade, 33, South Asian, black technical jacket and gloves, optic
down over his right eye, 100% matches the reference.

LOCATION MAP
Dead-centre one-point perspective down the corridor. Thin laser lines run
floor to ceiling and wall to wall at irregular angles across the full length.
Kade is in the midground, 5 metres from camera. The sealed door is in the far
background.

FIRST FRAME / BLOCKING
Kade already mid-step between two beams, body turned sideways, facing frame
left, symmetrical corridor composition.

FORMAT MODE
One continuous shot, the camera does not cut on its own.

OPTICS
63° field of view, rectilinear, deep focus, perfect symmetry.

CAMERA
Locked-off at standing height, dead centre.

ACTION
0.0s to 2.0s — Kade slides his right leg over a low beam at 0.5 km/h. 2.0s to
4.0s — he leans his torso back; a diagonal beam passes 5cm in front of his
face, lighting his stubble and the optic in thin blue. 4.0s to 5.0s — he
straightens on the far side of the beam, perfectly still, one breath.

PERFORMANCE
Total control: slow breath through the nose, jaw relaxed, eyes tracking the
beam. Skin detail sharp where the laser grazes it.

PHYSICS
The beams are fixed and perfectly straight. Dust particles glint as they
cross the beams. His body moves with balance and weight.

LIGHTING
Cold 6000K ceiling cove strips at low level, the blue laser lines as the main
visual light, a thin blue graze across his face as the beam passes.

COLOR GRADE
Steel grey, black and electric blue lines.

AUDIO
Silence apart from his breath and one faint electrical hum.

STYLE
Photoreal thriller cinematography, fine grain, 24 fps real time.

POSITIVE LOCKS
Every laser line stays perfectly straight and passes in front of him, never
through him. The corridor stays symmetrical. No text or signage.
```

---

## V06 · 0:13–0:16 · The vault, the empty case · generate 5s · ★ HARD
**First frame:** `@k_vault` (K1). **Refs:** `@vault`, `@nova`, `@case`, `@kadeblack`

```
SCENE CONTEXT
A circular black marble vault, one shaft of cold light on a plinth where the
NOVA bottle stands alone. A thief steps out of the darkness, sets a black
briefcase flat on the plinth beside the bottle and opens it. Inside, the blue
velvet holds an empty bottle-shaped cavity.

ACTIVE REFERENCES
@vault: the circular black marble vault with the single dome aperture and the
80cm plinth, 100% matches the reference.
@nova: the sapphire crystal bottle at the plinth centre — faceted ovoid,
hollow spherical void, luminous blue liquid, eight-spike star cap, 100%
matches the reference.
@case: matte black carbon fibre attaché case, gunmetal corners, navy leather
handle; inside, pristine deep blue velvet with one empty bottle-shaped cavity,
100% matches the reference.
@kadeblack: Kade, 33, South Asian, black technical jacket, black gloves, optic
pushed up on his forehead, 100% matches the reference.

LOCATION MAP
Centre: plinth with the bottle in the light shaft. Left of frame: darkness
Kade walks out of. Camera faces the plinth from 3 metres, chest height,
angled 15 degrees down so the plinth top is visible.

FIRST FRAME / BLOCKING
Exactly the provided first frame: bottle alone on the plinth, dark empty floor
on the left.

FORMAT MODE
One continuous shot, the camera does not cut on its own.

OPTICS
47° field of view, rectilinear, focus on the plinth top.

CAMERA
Locked-off tripod, the frame does not move at all.

ACTION
0.0s to 1.5s — Kade walks out of the darkness from frame left at 3 km/h,
carrying the case at his side, his face in shadow. 1.5s to 3.0s — he stops at
the plinth and lays the case flat on the plinth top to the left of the
bottle, 20cm from it. 3.0s to 5.0s — he unlatches it and lifts the lid away
from camera; the interior faces camera: blue velvet with a precise empty
bottle-shaped cavity, clearly empty. The bottle stands untouched in the light.

PHYSICS
The case has weight and sits flat with a contact shadow. Latches snap open
with a small recoil. Dust drifts through the light shaft.

LIGHTING
One hard vertical shaft of 7000K light from the dome onto the plinth; Kade
enters from darkness into its edge; the rest of the vault falls to navy black.

COLOR GRADE
Deep navy shadows, electric sapphire glow in the bottle, platinum highlights
on metal.

AUDIO
Heavy slow score, footsteps echoing on marble, two latch clicks.

STYLE
Photoreal heist cinema, fine grain, 24 fps real time.

POSITIVE LOCKS
The camera frame is identical from first to last frame. The bottle stays
standing at the plinth centre the whole shot. The case interior is empty
velvet with the bottle-shaped cavity clearly visible. No text anywhere.
```

---

## V07 · 0:16–0:18 · The star on his face · generate 5s · ★ HARD
**Refs:** `@kadeblack`, `@nova`, `@caustic` (optional). **Backup:** if the star won't form, regenerate with just a blue glow on the face and composite the star in AE from the `@caustic` sheet.

```
SCENE CONTEXT
Inside the dark vault, a thief lifts a crystal perfume bottle up into a shaft
of light at face height. The light passing through the bottle's hollow core
throws an eight-armed star onto his face. This is the first time we see his
face clearly.

ACTIVE REFERENCES
@kadeblack: Kade, 33, South Asian, pale scar through the left eyebrow, grey
streak at the right temple, three-day stubble, black technical jacket, thin
black gloves, 100% matches the reference.
@nova: the sapphire crystal bottle — faceted ovoid with a hollow spherical
void through its centre, luminous blue liquid, eight-spike metal star cap,
100% matches the reference.

LOCATION MAP
Kade faces camera in the centre. The bottle is held in his right gloved hand
between the camera and his face, low in frame left. The vertical light shaft
comes from above and slightly behind the bottle. Background: black marble
falling to darkness.

FIRST FRAME / BLOCKING
MCU of Kade, face half in darkness, the bottle rising into frame from below.

FORMAT MODE
One continuous shot, the camera does not cut on its own.

OPTICS
29° field of view, portrait compression, focus on his eyes.

CAMERA
Locked-off at eye level, 1.2 metres from his face.

ACTION
0.0s to 1.5s — Kade raises the bottle into the light shaft at chin height.
1.5s to 3.5s — light passes through the hollow core and projects an
eight-armed star with a dark centre across his face, the dark centre over the
bridge of his nose, the arms spreading across his cheekbones and brow. 3.5s to
5.0s — he holds completely still, eyes on the bottle, the star steady on his
skin.

PERFORMANCE
Calm, almost reverent. Eyes steady and unblinking, a slow exhale, the
smallest tightening at the corner of the mouth. Pore-level skin, stubble
catching the blue light, living catch-lights in both eyes.

PHYSICS
The star is a real optical caustic: fine threads at the arm edges, bending
over the curves of his face, moving slightly as his hand breathes.

LIGHTING
One hard 7000K beam from above through the bottle; the star pattern is the
key light on his face; everything else black.

COLOR GRADE
Electric sapphire and cyan in the star, deep navy shadows, warm brown skin
held natural under the blue.

AUDIO
The first big score swell with a deep sub-bass hit.

STYLE
Photoreal cinematic portrait, fine grain, 24 fps real time.

POSITIVE LOCKS
Face matches the reference exactly: eyebrow scar, grey temple streak. The
star has eight arms and a dark centre. One bottle, in his right hand.
```

---

## V08 · 0:18–0:20 · Product macro block · generate 5s
**Refs:** `@nova` (attach the A3 macro sheet too if you made it)

```
SCENE CONTEXT
Three extreme macro product details of the NOVA perfume bottle in darkness.

ACTIVE REFERENCES
@nova: the sapphire crystal bottle — forty flat facets, hollow spherical void,
luminous blue liquid, brushed blue-silver collar with turning marks,
eight-spike star-burst metal cap, small engraved eight-pointed star emblem on
the base, 100% matches the reference.

FORMAT MODE
Timed multishot, cuts only at the specified points, the camera does not cut on
its own.

0.0s to 1.6s — ECU, 12° field of view, light sliding across the crystal
facets, blue liquid shifting slowly behind the glass, one small air bubble
drifting up.
1.6s HARD CUT
1.6s to 3.3s — ECU, 12° field of view, low angle on the eight-spike metal star
cap, a sliver of light travelling along each spike.
3.3s HARD CUT
3.3s to 5.0s — ECU, 12° field of view, the flat base, the engraved
eight-pointed star emblem catching a raking light.
No drift mid-segment.

CAMERA
Slow motorised slide at 0.2 km/h across each detail, focus stacked and
tack sharp.

PHYSICS
Liquid moves with real viscosity. Light refracts through the facets
accurately.

LIGHTING
One hard raking 7000K light per detail against black.

COLOR GRADE
Sapphire blue glass, platinum metal, black surround.

AUDIO
Score holding, a single glass tap.

STYLE
Photoreal luxury product macro, focus-stacked clarity, 24 fps real time.

POSITIVE LOCKS
The bottle matches the reference in every segment. No text or letters
anywhere, only the star emblem on the base.
```

---

## V09A · 0:20–0:21.5 · The spray on the wrist · generate 5s
**Refs:** `@kadeblack`, `@nova`

```
SCENE CONTEXT
Inside the vault, a thief pulls back his jacket cuff, sprays the NOVA perfume
once onto his bare wrist, and breathes it in.

ACTIVE REFERENCES
@kadeblack: Kade, 33, South Asian, black technical jacket, thin black gloves
ending at the wrist bone, 100% matches the reference.
@nova: the sapphire crystal bottle with the eight-spike star cap removed,
revealing the fine metal atomizer nozzle, 100% matches the reference.

LOCATION MAP
Kade stands at the plinth in the light shaft, three-quarter to camera facing
frame right. His left wrist is raised at chest height, the bottle in his right
hand 10cm from it.

FIRST FRAME / BLOCKING
MCU: his gloved right hand holding the bottle, his left wrist bare where the
jacket cuff is pulled back, his face soft in the upper frame.

FORMAT MODE
One continuous shot, the camera does not cut on its own.

OPTICS
29° field of view, focus on the wrist and nozzle, face softly out of focus.

CAMERA
Locked-off at chest height.

ACTION
0.0s to 1.5s — one press of the atomizer: a fine mist cone hits the inside of
the bare wrist. 1.5s to 3.5s — the mist glows blue in the light and settles
on the skin. 3.5s to 5.0s — he lifts the wrist toward his face, eyes closing,
one slow breath in.

PERFORMANCE
Eyes close slowly, shoulders drop a millimetre, a long inhale through the
nose. Pore-level skin on the wrist, fine hair lifting in the mist.

PHYSICS
Real atomized droplets, backlit, sharp at the front edge and hazy behind;
droplets bead on the skin.

LIGHTING
Hard 7000K overhead shaft, the mist glowing electric blue against the dark.

COLOR GRADE
Navy black, cyan-blue mist, warm natural skin.

AUDIO
One crisp spray, one long breath in.

STYLE
Photoreal intimate close-up, fine grain, 24 fps real time.

POSITIVE LOCKS
Exactly one spray. The wrist is bare skin. The bottle stays in his right hand.
```

---

## V09B · 0:21.5–0:24 · Bottle goes BACK · generate 5s · ★★ THE KEY SHOT
**First frame:** `@k_vault` (K1). **Refs:** `@vault`, `@nova`, `@case`, `@kadeblack`. Regenerate until the "set down" is unmistakable.

```
SCENE CONTEXT
In the vault, a thief sets the perfume bottle deliberately back on its plinth
exactly where it stood, closes his empty briefcase, and walks away. The
bottle stays behind.

ACTIVE REFERENCES
@vault: the circular black marble vault and 80cm plinth, 100% matches the
reference.
@nova: the sapphire crystal bottle, faceted ovoid with a hollow core, blue
liquid, eight-spike star cap back on, 100% matches the reference.
@case: the matte black carbon fibre case, lying open flat on the plinth top
left of centre, its blue velvet cavity EMPTY, 100% matches the reference.
@kadeblack: Kade, 33, South Asian, black technical jacket, black gloves, 100%
matches the reference.

LOCATION MAP
Plinth centre frame in the light shaft. The open empty case lies on the left
half of the plinth top. Kade stands behind the plinth facing camera, holding
the bottle in his right hand just above the plinth centre.

FIRST FRAME / BLOCKING
Medium shot: Kade behind the plinth, bottle held 15cm above its marked spot,
open empty case beside it.

FORMAT MODE
One continuous shot, the camera does not cut on its own.

OPTICS
47° field of view, focus on the plinth top.

CAMERA
Locked-off at chest height, angled 15 degrees down.

ACTION
0.0s to 1.2s — Kade lowers the bottle slowly and sets it down upright at the
exact centre of the plinth; the base touches the stone and his gloved fingers
open and lift away. 1.2s to 2.0s — nothing moves; the bottle stands alone in
the light. 2.0s to 3.5s — he closes the lid of the empty case, snaps both
latches, and lifts it by the handle. 3.5s to 5.0s — he turns and walks out of
frame left at 3 km/h; the light in the vault shifts to a slow pulsing deep red
at 30% intensity, and the bottle stays standing at the centre in its shaft of
light.

PERFORMANCE
Unhurried, precise, zero hesitation. His face stays calm.

PHYSICS
The bottle lands with weight and a tiny contact settle, a real contact
shadow. The case closes with inertia; latches recoil.

LIGHTING
Hard 7000K overhead shaft on the plinth; after 3.5s a deep red pulse washes
the walls while the shaft on the bottle stays cold white-blue.

COLOR GRADE
Navy black, sapphire bottle, red alarm glow on the marble walls only.

AUDIO
The glass "tok" of the base on stone, a held silence, two latch clicks,
footsteps, a low alarm hum rising.

STYLE
Photoreal heist cinema, fine grain, 24 fps real time.

POSITIVE LOCKS
The bottle ends the shot standing upright at the plinth centre, in frame and
in focus. The case stays empty from start to finish. The camera frame never
moves.
```

---

## V10 · 0:24–0:28 · The roof: he hands them the case · generate 5s · ★ HARD
**Refs:** `@roof`, `@kaderain`, `@case`

```
SCENE CONTEXT
A rain-soaked rooftop forty storeys up at night. Guards burst through the roof
door with torches and catch a man in a long black overcoat holding a
briefcase. He stops, calmly slides the case across the wet concrete to their
feet, and steps back into the rain and darkness.

ACTIVE REFERENCES
@roof: the flat wet concrete rooftop with the steel access door on the left,
100% matches the reference.
@kaderain: Kade, 33, South Asian, long soaked black wool overcoat, wet hair
pushed back, bare hands, 100% matches the reference.
@case: the closed matte black carbon fibre case with gunmetal corners, 100%
matches the reference.

LOCATION MAP
Frame left: the steel roof door, three guards as backlit black silhouettes
with torches. Centre: open wet concrete with puddles. Frame right: Kade, 6
metres from the guards, facing them, the case in his right hand. Background:
blurred city skyline in rain.

FIRST FRAME / BLOCKING
The roof door already flung open, torch beams cutting across the rain onto
Kade on the right.

FORMAT MODE
One continuous shot, the camera does not cut on its own.

OPTICS
84° field of view, rectilinear.

CAMERA
Handheld at waist height, low over the concrete, small natural shake, camera
on the shadow side behind Kade's right shoulder looking toward the door.

ACTION
0.0s to 1.0s — torch beams find Kade; he stops walking. 1.0s to 2.5s — he
bends slightly and slides the closed case along the wet concrete toward the
guards; it skids 5 metres at 8 km/h, throwing a spray of water, and stops at
their feet. 2.5s to 4.0s — two guards lunge for the case. 4.0s to 5.0s — Kade
steps backward out of the torch beams into the rain and darkness.

PERFORMANCE
Kade is unhurried and unafraid; his posture stays upright, his hands open
after the release.

PHYSICS
Heavy rain streaks, splashes from every impact. The case slides with weight,
fans water, and slows with friction. The overcoat is heavy and dripping.

LIGHTING
Hard white torch beams from the door at 6000K cutting through the rain, the
guards pure silhouettes against the doorway, a cold blue city glow behind.

COLOR GRADE
Black and navy, white torch beams, blue skyline.

AUDIO
Rain, distant sirens, the case scraping and skidding, the score at its peak.

STYLE
Photoreal action thriller, fine grain, 24 fps real time.

POSITIVE LOCKS
The guards are backlit silhouettes with no faces visible. The case stays
closed. Kade ends the shot disappearing into the dark on the right.
```

---

## V11 · 0:28–0:29 · Mist transition (gold) · generate 5s
**Refs:** none. **Edit trick:** same as V02, cut out of V10 at the densest mist and straight into V12.

```
SCENE CONTEXT
Extreme close studio shot: a single burst of fine mist fires toward the lens
and fills the frame with warm gold light.

LOCATION MAP
Pure black void, one hard warm backlight behind the plume.

FIRST FRAME / BLOCKING
Black frame, a tight mist cone beginning at the bottom centre.

FORMAT MODE
One continuous shot, the camera does not cut on its own.

OPTICS
63° field of view, focus on the plume's leading edge.

CAMERA
Pushes forward into the plume at 6 km/h.

ACTION
0.0s to 2.0s — the mist fires and opens toward the lens. 2.0s to 5.0s — the
plume fills the frame edge to edge in a glowing amber-gold veil.

PHYSICS
Real atomized droplets, backlit, slowing in the air.

LIGHTING
One hard tungsten backlight at 2800K.

COLOR GRADE
Amber and old gold in the droplets, black surround.

AUDIO
The score cuts to silence; a single low tungsten hum.

STYLE
High-speed macro photography look, photoreal, 48 fps slow motion.

POSITIVE LOCKS
Only mist and black in frame, ending fully gold.
```

---

## V12 · 0:29–0:32 · Solen opens the empty case · generate 5s · ★ HARD
**First frame (optional):** the case closed on the table. **Refs:** `@goldroom`, `@solen`, `@caseempty`, `@case`

```
SCENE CONTEXT
In a dark oak study under one brass lamp, an older collector unlatches the
recovered briefcase on his table and lifts the lid. It is empty: only a
bottle-shaped cavity in blue velvet. Cut to his face. He says nothing.

ACTIVE REFERENCES
@goldroom: the oak-panelled study, round dark table, brass pendant lamp,
cigar smoke, 100% matches the reference.
@solen: Solen, 58, heavy-set, silver hair combed flat, pale blue deep-set
eyes, charcoal waistcoat, sleeves rolled, plain gold signet ring on the right
little finger, 100% matches the reference.
@caseempty: the open matte black case, pristine blue velvet with an empty
bottle-shaped cavity, 100% matches the reference.

FORMAT MODE
Timed multishot, cuts only at the specified points, the camera does not cut on
its own.

0.0s to 3.0s — high angle 47° field of view looking straight down into the
case on the table. Solen's hands with the signet ring flip both latches and
raise the lid. The interior faces camera: blue velvet, one precise empty
bottle-shaped cavity, nothing else. The lid LED lights the empty cavity.
3.0s HARD CUT
3.0s to 5.0s — MCU, 29° field of view, Solen's face lit from the lamp above,
looking down into the case.
No drift mid-segment.

CAMERA
Locked-off in both segments.

PERFORMANCE
Solen: the eyes stay down on the case, the jaw sets, one slow blink, a
nostril flares. Stillness. Pore-level skin, broken capillaries, sweat sheen
under the hot lamp.

PHYSICS
Heavy lid, latches with recoil, cigar smoke drifting in the lamp light.

LIGHTING
One hot 2800K tungsten pendant directly above the table; everything outside
its pool in deep shadow.

COLOR GRADE
Old gold, amber and dark oak; the only blue is the velvet inside the case.

AUDIO
Two latch clicks, then complete silence. No music.

STYLE
Photoreal noir drama, fine grain, 24 fps real time.

POSITIVE LOCKS
The case is empty in every frame, velvet pristine, cavity clearly
bottle-shaped. Solen matches the reference. No text anywhere.
```

---

## V13 · 0:32–0:34 · The bottle is still there · generate 5s
**First frame:** `@k_vault` (K1). **Refs:** `@vault`, `@nova`

```
SCENE CONTEXT
The empty vault, silent. The NOVA bottle still stands alone on its plinth in
the shaft of light. Nothing was taken.

ACTIVE REFERENCES
@vault: the circular black marble vault and 80cm plinth, 100% matches the
reference.
@nova: the sapphire crystal bottle standing upright at the plinth centre,
eight-spike star cap on, 100% matches the reference.

FIRST FRAME / BLOCKING
Exactly the provided first frame, held.

FORMAT MODE
One continuous shot, the camera does not cut on its own.

OPTICS
47° field of view, focus on the bottle.

CAMERA
Locked-off tripod, the frame is identical from first to last frame.

ACTION
0.0s to 5.0s — the only motion is fine dust drifting slowly down through the
light shaft at 20% density and a faint shimmer of the blue liquid inside the
bottle.

PHYSICS
Dust falls with air resistance, sparkling as it crosses the beam.

LIGHTING
One hard 7000K vertical shaft on the bottle, everything else navy black.

COLOR GRADE
Deep navy, electric sapphire bottle, platinum cap highlights.

AUDIO
Silence and faint room tone.

STYLE
Photoreal, fine grain, 24 fps real time.

POSITIVE LOCKS
No people, no case. The bottle stands upright at the plinth centre for the
whole shot, sharp and clearly visible.
```

---

## V14A · 0:34–0:37 · The walk, Vero turns · generate 5s · ★ HARD
**Refs:** `@atrium`, `@kaderain`, `@verogown`

```
SCENE CONTEXT
The gala upstairs is still going as if nothing happened. The thief, in a wet
black overcoat, walks calmly through the black-tie crowd toward the exit. The
woman in the midnight blue gown passes him, takes two steps, stops, and turns
back as she catches his scent.

ACTIVE REFERENCES
@atrium: the marble gallery atrium with the chandeliers and brass balconies,
100% matches the reference.
@kaderain: Kade, 33, South Asian, long soaked black wool overcoat, wet hair
pushed back, grey streak at the right temple, 100% matches the reference.
@verogown: Vero, 31, dark hair in a low twisted knot, mole on the right
cheekbone, floor-length midnight blue silk gown, 100% matches the reference.

LOCATION MAP
Kade walks away from camera through the centre of the crowd toward the far
doors. Vero walks toward camera along frame right, passing Kade shoulder to
shoulder in the midground. Guests in black mingle in the foreground and
background.

FIRST FRAME / BLOCKING
Camera 2 metres behind Kade's back, following; Vero visible ahead on the
right, walking toward him; guests moving from frame one.

FORMAT MODE
One continuous shot, the camera does not cut on its own.

OPTICS
47° field of view, focus riding on Kade then on Vero.

CAMERA
Steadicam follow behind Kade at 3 km/h, chest height.

ACTION
0.0s to 1.5s — Kade walks steadily through the crowd, water still dripping
from his coat hem. 1.5s to 2.5s — Vero passes him on his right, shoulders
nearly brushing. 2.5s to 5.0s — Vero takes two more steps, slows, stops, and
turns her head and shoulders back over her left shoulder toward him, eyes
half closing, lips slightly parted. Kade keeps walking without looking back.

PERFORMANCE
Vero: a small intake of breath through the nose, eyelids lowering, the
faintest recognition at the corner of her mouth. Kade: completely neutral,
unhurried. Pore-level skin on both, living catch-lights from the chandeliers.

PHYSICS
Wet wool swings heavily and drips. Silk gown twists with her turn and settles
with weight.

LIGHTING
Warm 3200K chandelier light from above, cool 7000K spill from the vitrine
area, damp highlights on Kade's hair and coat.

COLOR GRADE
Black crowd, midnight blue silk, amber chandelier accents, navy shadows.

AUDIO
The gala murmur distant and softened, a single soft sustained note.

STYLE
Photoreal luxury cinema, fine grain, 24 fps real time.

POSITIVE LOCKS
Kade and Vero both match their references exactly. Kade keeps walking away;
Vero ends the shot turned back toward him.
```

---

## V14B · 0:37–0:38 · Insert: cuff over the wrist · generate 5s
**Refs:** `@kaderain`

```
SCENE CONTEXT
Insert close-up: as he walks, the man tugs his overcoat cuff down over his
left wrist; a faint blue shimmer glints on the skin where the perfume was
sprayed.

ACTIVE REFERENCES
@kaderain: Kade's left hand and wrist, bare skin, the cuff of a soaked black
wool overcoat, 100% matches the reference.

FIRST FRAME / BLOCKING
ECU of his left wrist at hip height mid-walk, the cuff pulled up 3cm.

FORMAT MODE
One continuous shot, the camera does not cut on its own.

OPTICS
18° field of view, shallow focus on the wrist.

CAMERA
Handheld tracking alongside at 3 km/h.

ACTION
0.0s to 2.0s — a faint cool blue shimmer catches on the inside of the bare
wrist as it passes under the light. 2.0s to 4.0s — his right fingers tug the
wet cuff down over it. 4.0s to 5.0s — his hand swings on with the walk.

PHYSICS
Wet wool with weight and drips; natural arm swing.

LIGHTING
Warm 3200K chandelier fill, a thin cool 7000K glint on the wrist.

AUDIO
The soft single note continues.

STYLE
Photoreal close-up, fine grain, 24 fps real time.

POSITIVE LOCKS
The wrist shows bare skin with only a subtle blue shimmer. No watch, no
jewellery, no symbols on the skin.
```

---

## V15 · 0:38–0:42 · Hero bottle + end card · generate 5s
**First frame (optional):** `@k_hero` (K2). **Refs:** `@nova`. Type the text in AE: *They took the case. He took NOVA.* → **NOVA** · EAU DE PARFUM.

```
SCENE CONTEXT
The NOVA perfume bottle alone in a black void, light passing through its
hollow core throws an eight-armed star onto the wall behind it; the camera
orbits very slowly.

ACTIVE REFERENCES
@nova: the sapphire crystal bottle — forty facets, hollow spherical void
through the centre, luminous blue liquid, brushed blue-silver collar,
eight-spike metal star cap, 100% matches the reference.

LOCATION MAP
Bottle centred slightly low on an invisible glossy black surface. A matte
black wall 1 metre behind it. One hard light behind and above the bottle.

FIRST FRAME / BLOCKING
The bottle centred, the star projected on the wall behind it.

FORMAT MODE
One continuous shot, the camera does not cut on its own.

OPTICS
29° field of view, focus on the bottle, the wall star softly defined.

CAMERA
Very slow orbit left to right around the bottle at 0.5 km/h, eye level to the
bottle.

ACTION
0.0s to 3.0s — the orbit reveals the facets catching the light; the star on
the wall shifts subtly with the angle. 3.0s to 5.0s — the backlight dims
slowly, the star fades to darkness, leaving the bottle glowing faintly blue.

PHYSICS
Real optical caustic with fine threads; glossy reflection of the base below.

LIGHTING
One hard cold 7500K backlight through the hollow core, a thin rim on the cap
spikes.

COLOR GRADE
Deep navy to electric sapphire, platinum metal, black void.

AUDIO
The final note, then one crisp spray sound, then black silence.

STYLE
Photoreal luxury product film, fine grain, 24 fps real time.

POSITIVE LOCKS
The bottle matches the reference exactly. The star has eight arms and a dark
centre. Empty black space in the lower third. No text anywhere in the image.
```

---

# PART E — EDIT ASSEMBLY IF YOU USE SINGLE SHOTS

| Order | Clip | Trim to | Note |
|---|---|---|---|
| 1 | V01 | 3.0s | end on the splash |
| 2 | V02 | 2.0s | cut V01 → mist → V03 at the whiteout |
| 3 | V03 | 4.0s | keep the whole plinth descent |
| 4 | V04 | 2.0s | ~0.6s per segment |
| 5 | V05 | 2.0s | breath only, no music |
| 6 | V06 | 3.0s | end on the empty case open |
| 7 | V07 | 2.0s | the star on the face |
| 8 | V08 | 2.0s | ~0.6s per insert |
| 9 | V09A | 1.5s | spray + inhale |
| 10 | V09B | 2.5s | **hold on the bottle after it's set down** |
| 11 | V10 | 4.0s | the case slide |
| 12 | V11 | 1.0s | gold whiteout into V12 |
| 13 | V12 | 3.0s | **silence** |
| 14 | V13 | 2.0s | silence |
| 15 | V14A | 3.0s | end on Vero's turn |
| 16 | V14B | 1.0s | cuff insert |
| 17 | V15 | 4.0s | text in AE, final spray sound |

**Total: 42.0s.** Titles are typed in After Effects. Before posting, run the blind test and the submission checklist in the bible.
