# NOVA — Seedance 2.5 prompts with @image slots
### One 30s clip + one 15s clip = 45s ad

The references are numbered in the same order they were made in the image-generation sequence (A1 → A17, then the K1 keyframe). Upload them into Seedance **in exactly this slot order**, so that `@image1` in the prompt is the first image you attached, `@image2` the second, and so on.

## Master image list (image-generation order)

| Gen step | Saved as | What it is |
|---|---|---|
| A1 | `@nova` | Bottle turnaround |
| A2 | — | Bottle in-context (reference only, not attached to video) |
| A3 | — | Bottle macros (optional) |
| A4 | `@case` | Briefcase sheet |
| A5 | `@caseempty` | Empty case reveal |
| A6 | `@kade` | Kade base face (used only to make A7/A8) |
| A7 | `@kadeblack` | Kade, vault wardrobe |
| A8 | `@kaderain` | Kade, overcoat |
| A9 | `@vero` | Vero base face (used only to make A10) |
| A10 | `@verogown` | Vero, gown |
| A11 | `@solen` | Solen |
| A12 | `@vault` | Vault plate (used only to make K1) |
| A13 | `@atrium` | Atrium plate |
| A14 | `@corridor` | Corridor plate (described in text, not attached) |
| A15 | `@roof` | Roof plate |
| A16 | `@goldroom` | Gold room plate (described in text, not attached) |
| A17 | `@street` | Street plate (described in text, not attached) |
| K1 | `@k_vault` | Vault keyframe: bottle on the plinth |
| K2 | `@k_hero` | Hero bottle keyframe (optional) |

---

## CLIP 1 · 30 seconds · street → atrium → vault → roof

| Slot | Upload this image | From step |
|---|---|---|
| **@image1** | NOVA bottle turnaround | A1 |
| **@image2** | Briefcase sheet | A4 |
| **@image3** | Kade, vault wardrobe | A7 |
| **@image4** | Vero, gown | A10 |
| **@image5** | Atrium plate | A13 |
| **@image6** | Roof plate | A15 |
| **@image7** | Vault keyframe (bottle on plinth) | K1 |

```
SCENE CONTEXT
A rain-soaked city at night. A man steps out of a car; a burst of blue perfume
mist; a black-tie gala where the NOVA perfume bottle glows in a vitrine and a
woman in a midnight blue gown watches the plinth sink into the floor; below, a
thief slips through a laser corridor into a circular black marble vault, opens
an empty briefcase beside the bottle, lifts the bottle into the light, sprays
it once on his bare wrist, sets the bottle BACK on the plinth, closes the empty
case and walks out; on the rooftop, guards corner him and he slides the case to
them and steps back into the rain.

ACTIVE REFERENCES
@image1: sapphire crystal perfume bottle — forty facets, hollow spherical void
through its centre, luminous blue liquid, brushed blue-silver collar,
eight-spike metal star cap, 100% matches the reference.
@image2: matte black carbon fibre attaché case, gunmetal corners, navy leather
handle; inside, pristine blue velvet with one EMPTY bottle-shaped cavity, 100%
matches the reference.
@image3: Kade, 33, South Asian, pale scar through the left eyebrow, grey
streak at the right temple, three-day stubble, matte black technical jacket,
thin black gloves ending at the wrist bone, matte black single-lens optic,
100% matches the reference.
@image4: Vero, 31, dark hair in a low twisted knot, small mole on the right
cheekbone, floor-length midnight blue silk gown, 100% matches the reference.
@image5: marble gallery atrium, black plinth with a glass vitrine, thin steel
floor ring around the plinth base, crystal chandeliers, 100% matches the
reference.
@image6: flat wet concrete rooftop forty storeys up, steel access door on the
left, blurred skyline in rain, 100% matches the reference.
@image7: the vault wide frame — circular black marble chamber, one dome
aperture dropping a vertical shaft of light onto an 80cm black marble plinth,
the bottle standing at the plinth centre, camera at chest height angled 15
degrees down, 100% matches the reference.

FORMAT MODE
Timed multishot, cuts only at the specified points, the camera does not cut on
its own. Every vault wide uses the identical locked frame of @image7.

0.0s to 3.0s — STREET. Wide 84°, camera locked 5cm above black wet asphalt, a
puddle with a blue reflection in the lower third, dark stone facades with
abstract blue-white signage glow behind. The rear door of a black unbadged
sedan on the right swings open; one black shoe steps into the puddle, the hem
of a soaked long black overcoat falls behind it, water splashes in a crown.
Only legs, shoe and coat hem in frame.
3.0s HARD CUT
3.0s to 5.0s — BLUE MIST. 63°, black void; a burst of fine atomized mist fires
toward the lens and the camera pushes into it at 6 km/h until the whole frame
is a glowing electric blue-white veil. 48 fps slow motion in this segment only.
5.0s HARD CUT
5.0s to 9.5s — ATRIUM. 63°, chest height, slow push-in at 2 km/h through a gap
in a black-tie crowd, the glowing vitrine with the NOVA bottle centred. 5.0s to
7.0s Vero walks in from frame left and stops one metre from the vitrine, eyes
fixed on the bottle. 7.0s to 9.5s the plinth, vitrine and bottle descend
smoothly into the steel floor ring at 0.3 km/h, the glow sinking with it;
Vero's gaze follows it down while guests keep moving.
9.5s HARD CUT
9.5s to 11.5s — MACROS. Three extreme close-ups, handheld: a black-gloved hand
pressing flat on a brushed-steel panel (12°); the matte black optic swinging
down over Kade's right eye, only eye socket and stubble in frame (18°); a thin
black fibre-optic cable sliding under a steel door gap at floor level (12°).
11.5s HARD CUT
11.5s to 13.5s — CORRIDOR. 63°, locked-off dead centre, one-point perspective
down a brushed stainless steel corridor. Thin blue laser lines cross it at
irregular angles. Kade, 5 metres away, turned sideways, leans back as a
diagonal beam passes 5cm in front of his face, grazing his stubble in blue.
13.5s HARD CUT
13.5s to 16.5s — VAULT WIDE, the exact @image7 frame, 47°, locked-off. Kade
walks out of the darkness from frame left at 3 km/h carrying the closed case,
lays it flat on the plinth top 20cm left of the bottle, unlatches it and lifts
the lid away from camera: the blue velvet interior faces camera, one precise
bottle-shaped cavity, clearly empty. The bottle stands untouched.
16.5s HARD CUT
16.5s to 18.5s — FACE. MCU 29°, locked at eye level. Kade raises the bottle
into the light shaft at chin height; light through the hollow core projects an
eight-armed star with a dark centre across his face, the dark centre on the
bridge of his nose, the arms over cheekbones and brow. He holds completely
still, eyes on the bottle.
18.5s HARD CUT
18.5s to 20.0s — PRODUCT. Two extreme close-ups, 0.75s each, 12°: light sliding
across the crystal facets with the blue liquid shifting; the eight-spike metal
star cap from a low angle, light travelling along each spike.
20.0s HARD CUT
20.0s to 21.5s — SPRAY. MCU 29°. Cap off, his gloved right hand holds the
bottle 10cm from his bare left wrist; one press, a fine mist cone hits the
inside of the wrist glowing blue; he lifts the wrist toward his face, eyes
closing, one breath in.
21.5s HARD CUT
21.5s to 25.0s — VAULT WIDE, the exact @image7 frame again, locked-off, the
open empty case on the left of the plinth top. 21.5s to 22.7s Kade, cap back
on, sets the bottle down upright at the exact centre of the plinth; the base
touches the stone and his gloved fingers open and lift away. 22.7s to 23.3s
nothing moves; the bottle stands alone in the light. 23.3s to 24.2s he closes
the empty case, snaps the latches and lifts it. 24.2s to 25.0s he walks out of
frame left as the vault walls wash in deep pulsing red; the bottle stays
standing at the plinth centre.
25.0s HARD CUT
25.0s to 30.0s — ROOF. 84°, handheld at waist height behind Kade's right
shoulder. Kade now wears a long soaked black wool overcoat, wet hair pushed
back, the closed case in his right hand. The steel door on the left is flung
open; three guards as pure backlit black silhouettes aim torches at him from 6
metres. 25.0s to 26.0s the beams find him and he stops. 26.0s to 27.5s he
slides the case along the wet concrete toward them; it skids 5 metres at 8 km/h
throwing water and stops at their feet. 27.5s to 29.0s two guards lunge for it.
29.0s to 30.0s Kade steps backward out of the beams into the rain and darkness.
No drift mid-segment.

PERFORMANCE
Vero: composed and still, desire only in her eyes and one small breath.
Kade: total calm and control, slow breath through the nose, no hesitation, an
almost reverent stillness when the star lands on his face, unhurried on the
roof. Pore-level skin, living catch-lights.

PHYSICS
Rain rings the puddles; the plinth moves as one heavy mechanical unit; laser
lines stay perfectly straight and pass in front of him; the case has weight
and latches recoil; mist droplets are real, backlit and bead on skin; the
bottle lands with weight and a real contact shadow; the case skids with
friction and fans water; the wet overcoat swings heavily.

LIGHTING
Street: cold 8500K signage spill from frame left. Atrium: cold 7000K vitrine
glow on the bottle and Vero's face, warm 3200K chandelier fill. Corridor: low
6000K cove strips with blue laser lines. Vault: one hard 7000K vertical shaft
on the plinth, everything else navy black, the star caustic as the key on his
face, red alarm wash on the walls only at the end. Roof: hard white 6000K
torch beams through rain, guards pure silhouettes, cold blue skyline.

COLOR GRADE
Navy and black throughout, electric sapphire and cyan in the glass, mist and
lasers, platinum metal highlights, warm amber only in the chandeliers, natural
warm skin under blue.

AUDIO
Rain, a car door, a splash and a low drone; an atomizer spray and whoosh; gala
murmur and hydraulic hum; metal and servo clicks; silence and breath in the
corridor; footsteps and latch clicks in the vault; a big score swell on the
face; one spray and an inhale; the glass "tok" of the bottle on stone and held
silence; latches, footsteps, alarm hum; rain, sirens and the case skidding with
the score at its peak.

STYLE
Photoreal luxury heist cinema, fine film grain, 24 fps real time except the
mist segment.

POSITIVE LOCKS
The man's face stays unseen on the street. One bottle only: in the vitrine at
the gala, and on the vault plinth where it ends standing upright after he
leaves. The case is empty from start to finish and closed on the roof. The
vault wide frame is identical both times. Kade's face matches the reference:
eyebrow scar, grey temple streak. Vero matches the reference. Guards are
faceless silhouettes. The car is unbadged, signage is abstract light, and no
readable text appears anywhere.
```

---

## CLIP 2 · 15 seconds · gold room → vault → gala → end card

| Slot | Upload this image | From step |
|---|---|---|
| **@image1** | NOVA bottle turnaround | A1 |
| **@image2** | Empty case reveal | A5 |
| **@image3** | Kade, overcoat | A8 |
| **@image4** | Vero, gown | A10 |
| **@image5** | Solen | A11 |
| **@image6** | Vault keyframe (bottle on plinth) | K1 |

**End card text (type in After Effects over 11–15s):** *They took the case. He took NOVA.* → **NOVA** · EAU DE PARFUM

```
SCENE CONTEXT
A burst of gold mist; in a dark oak study the collector opens the recovered
briefcase and finds it empty; the silent vault where the NOVA bottle still
stands on its plinth; the gala upstairs, where the thief in a wet overcoat
walks through the crowd and the woman in the blue gown turns back as she
catches his scent; he tugs his cuff over his wrist; the NOVA bottle alone in a
black void, throwing a star of light on the wall behind it.

ACTIVE REFERENCES
@image1: sapphire crystal perfume bottle — forty facets, hollow spherical void,
luminous blue liquid, brushed blue-silver collar, eight-spike metal star cap,
100% matches the reference.
@image2: the open matte black case, pristine blue velvet with one empty
bottle-shaped cavity lit by the LED in the lid, 100% matches the reference.
@image3: Kade, 33, South Asian, long soaked black wool overcoat, wet hair
pushed back, grey streak at the right temple, bare hands, 100% matches the
reference.
@image4: Vero, 31, dark hair in a low twisted knot, mole on the right
cheekbone, floor-length midnight blue silk gown, 100% matches the reference.
@image5: Solen, 58, heavy-set, silver hair combed flat, pale blue deep-set
eyes, charcoal waistcoat, sleeves rolled, plain gold signet ring on the right
little finger, 100% matches the reference.
@image6: the vault wide frame — circular black marble chamber, one vertical
shaft of light onto an 80cm black marble plinth, the bottle standing at the
plinth centre, camera at chest height angled 15 degrees down, 100% matches the
reference.

FORMAT MODE
Timed multishot, cuts only at the specified points, the camera does not cut on
its own.

0.0s to 1.0s — GOLD MIST. 63°, black void, a burst of fine mist fires toward
the lens as the camera pushes in, filling the frame with glowing amber-gold.
48 fps slow motion in this segment only.
1.0s HARD CUT
1.0s to 3.5s — CASE. High angle 47°, locked, straight down onto a round dark
oak table under one brass pendant lamp, cigar smoke in the light. Solen's hands
with the signet ring flip both latches and raise the lid: pristine blue velvet,
one precise empty bottle-shaped cavity, nothing else, lit by the lid LED.
3.5s HARD CUT
3.5s to 5.0s — SOLEN. MCU 29°, locked. He looks down into the case under the
hot lamp: eyes fixed, jaw sets, one slow blink, a nostril flares. Complete
stillness.
5.0s HARD CUT
5.0s to 7.0s — VAULT, the exact @image6 frame, locked-off tripod: the empty
vault, no one in it, the bottle still standing upright at the plinth centre in
its cold shaft of light, fine dust drifting down through the beam.
7.0s HARD CUT
7.0s to 10.0s — WALK. 47°, steadicam 2 metres behind Kade at chest height,
following at 3 km/h through a black-tie crowd in the marble atrium under warm
crystal chandeliers, water dripping from his coat hem. 7.5s to 8.3s Vero,
walking toward camera on the right, passes him shoulder to shoulder. 8.3s to
10.0s she stops and turns her head and shoulders back over her left shoulder
toward him, eyes half closing, lips slightly parted. Kade keeps walking without
looking back.
10.0s HARD CUT
10.0s to 11.0s — CUFF. ECU 18°, tracking alongside. His bare left wrist
mid-walk; a faint cool blue shimmer catches on the inside of the wrist, then
his right fingers tug the wet overcoat cuff down over it.
11.0s HARD CUT
11.0s to 15.0s — HERO. 29°, a very slow orbit left to right at 0.5 km/h around
the NOVA bottle on a glossy black surface in a pure black void, centred
slightly low with empty black space in the lower third. One hard cold backlight
through the hollow core throws an eight-armed star with a dark centre onto a
matte black wall 1 metre behind. 13.0s to 15.0s the backlight dims and the star
fades, leaving the bottle glowing faintly blue.
No drift mid-segment.

PERFORMANCE
Solen: stillness, anger held behind the eyes; sweat sheen under the lamp,
broken capillaries. Vero: a small intake of breath through the nose, eyelids
lowering, the faintest recognition at the corner of her mouth. Kade: neutral
and unhurried. Pore-level skin, living catch-lights.

PHYSICS
Mist droplets slow in the air; the case lid lifts with weight; cigar smoke
drifts; dust falls through the vault beam; wet wool swings and drips; the silk
gown twists with her turn and settles; the star is a real optical caustic with
fine threads; glossy reflection under the bottle.

LIGHTING
Study: one hot 2800K tungsten pendant above the table, deep shadow outside its
pool. Vault: one hard 7000K vertical shaft, navy black around it. Atrium: warm
3200K chandeliers, damp highlights on Kade, a thin cool glint on the wrist.
Hero: one hard 7500K backlight through the bottle core, a thin rim on the cap
spikes.

COLOR GRADE
Mist and study in old gold, amber and dark oak, the only blue the velvet in
the case; vault in deep navy and electric sapphire; gala in black, midnight
blue silk and amber accents; hero in deep navy to electric sapphire with
platinum metal.

AUDIO
The score cuts dead into a low tungsten hum; two latch clicks then total
silence through the vault shot; a soft sustained note under the distant gala
murmur; the final note, one crisp spray sound, then black silence.

STYLE
Photoreal luxury cinema, fine film grain, 24 fps real time except the mist
segment.

POSITIVE LOCKS
The case is empty, velvet pristine, cavity clearly bottle-shaped. The vault
frame matches @image6 with the bottle standing upright and no people. Solen,
Kade and Vero match their references. Kade keeps walking; Vero ends turned back
toward him. The wrist is bare skin with only a subtle blue shimmer. No text
anywhere in the image.
```

---

**If Seedance caps the number of references:**
- **Clip 1:** drop @image6 (roof) first, then @image5 (atrium). Both places are also described in the text. Renumber the tags in the prompt to match what you uploaded.
- **Clip 2:** drop @image4 (Vero) last, because her turning back is the payoff of the film.
