# Client testimonial edits (from the Seedance clips)

Two finished 9:16 testimonials built from the clips you generated, both 1080 x 1920, 24 fps, 33 s (30 s of footage plus a 3 s end card), stereo AAC, mastered to -14 LUFS / about -2 dBTP. No personal name or job title appears on screen.

| File | Client | What it shows |
|---|---|---|
| `leam_taxis_testimonial_9x16.mp4` | Leam Taxis · leamingtonspa-taxis.co.uk | Desk intro with the site behind the speaker, then the monitor shot. His screen now shows a calls report with the running total of his real Google Business Profile calls, drawing on under his finger (details below). The selfie section uses the real site: hero, airport destinations, "For drivers / Become a driver". |
| `organic_fostering_testimonial_9x16.mp4` | Organic Fostering · organicfostering.co.uk | Interview with the site's trust ticks beside her and a search bar above. The blank laptop screen shows the real Areas page; it lifts off into a card, with site-fact chips and a Manchester card. The mug she lifts stays in front of the screen. In the close-up the footage shrinks into a window over the blog and enquiry pages, then opens back up for "Honestly, it's changed everything for us." |

## How the graphics sit with the people

- **Person mattes:** Robust Video Matting runs on every frame (`grp_prep.py mattes`). Website cards are placed behind the speakers, so heads and shoulders pass in front of them, and no text sits behind a face.
- **In front:** cursors, captions, the logo bug and the AI label.
- **Placement:** every card sits in clear space: above the speaker, beside the head, or in the free half of the desk shot. Nothing is placed over a face or the mug.

## The Leam monitor chart (why a running total)

His monthly calls are fairly flat (Business Profile, May–Oct 2026: about 19, 17, 20, 21, then 25 in September and 12 in part-month October; 114 in all). The generated finger sweeps steeply up the screen, and no honest monthly chart can follow it. The running total of the same calls (19 → 36 → 56 → 77 → 102 → 114) does climb steadily.

The screen shows that running total:
- It is clearly labelled, on a linear axis from 0.
- The month spacing and scale are fitted to the measured fingertip path, so the line draws on just under his finger.
- Only 114 and September's 25 are printed as exact figures. The other monthly points are read from the Business Profile chart, and the screen says so.
- October is marked as a part month.

## What is real in the graphics

- **Website captures:** `assets/sites/*` (captured 22 Oct 2026). The OF homepage photos of children are never shown; the trust-ticks card is set from the homepage text.
- **Data:** the Leam Business Profile calls screenshot `assets/gsc/leamingtonspa_gbp_calls_may-oct2026.png` (114 calls May–Oct 2026, September 25, October a part month).
- **OF site facts:** HTTPS, mobile-friendly pages, and 61 pages and 32 guides in `sitemap_20261022.xml`. "Based in Old Trafford" comes from the Areas page.
- **Logos:**
  - Organic Fostering: brand files.
  - Leam Taxis: a vector rebuild of the site logo.
  - Hulk Marketing: `assets/sites/hulkmarketing/hulk-marketing-logo.png`.

## Clean-up done on the generated footage

- **Leam shot 1:** a pint glass on the desk is cropped out.
- **Leam shot 2:** the made-up green screen and line are replaced, clipped to the monitor's real bezel, and his hand is composited back on top.
- **OF shot 1:** the fake banner lettering is painted out and feathered against her silhouette.
- **OF shot 3:** a small punch-in keeps the fake banner out of frame.
- **OF shot 2:** the laptop shows the real Areas page, with a per-frame occlusion matte for the mug and her fingers.

## Before you publish: claims that need evidence

The voices are AI-generated from the scripts. These spoken lines are claims, and UK advertising rules (CAP Code, and the DMCC Act 2024 on fake reviews) need them true and provable:

- **Leam Taxis**
  - "this is our Search Console … that's our clicks": the screen shows **Business Profile calls**. We had no Search Console export for Leam. Send one and we can swap it in, or the line should change.
  - "We're number one now for taxis in Leamington Spa": needs a dated ranking screenshot. We could not verify it.
  - "airport bookings are up", "I've had to take on more drivers": need the client's confirmation.
  - "Flat as a pancake … it just climbs": the monthly calls rise modestly, and the climbing line on screen is the running total (labelled). Confirm the client is happy with the wording.
  - Confirm the 114-calls profile is Leam Taxis'.
- **Organic Fostering**
  - "They rebuilt our website, fixed the technical side, and set up our Google profile for Manchester": confirm this was Hulk's work.
  - "we're on page one for the searches that matter", "enquiries come in every week": need evidence or the client's written confirmation.
- **Both:** each client's written OK for the AI re-creation of their likeness and words.

The videos carry an "AI re-creation" label throughout and end-card fine print ("Results vary by business"). No ranking badges, growth arrows or numbers were added beyond the real data above.

## Rebuild

```bash
cd pipeline/fostering
python3 grp_prep.py leam && python3 grp_prep.py of        # hand mattes + fingertip track, banner patches
python3 grp_prep.py oflap                                  # laptop occlusion (mug / fingers)
python3 grp_prep.py mattes leam && python3 grp_prep.py mattes of   # person mattes (needs workspace3/models/rvm_mobilenetv3_fp32.onnx)
python3 grp_audio.py all                                   # dialogue + SFX + original music -> workspace3/audio/grp
FOSTER_FPS=24 python3 render.py grp_leam --audio ../../workspace3/audio/grp/leam_mix.wav
FOSTER_FPS=24 python3 render.py grp_of   --audio ../../workspace3/audio/grp/of_mix.wav
```

The source clips go in `workspace3/frames/leam` and `workspace3/frames/of` (721 JPGs each), registered in `workspace3/frames/manifest.json`. Captions come from `edits/asr/*.json` (faster-whisper word timings, spelling fixes and retimes in the modules).
