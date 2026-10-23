# Client testimonial edits (from the Seedance clips)

Two finished 9:16 testimonials built from the clips you generated, both 1080 x 1920, 24 fps, 33 s (30 s of footage plus a 3 s end card), stereo AAC, mastered to -14 LUFS / -2 dBTP.

| File | Client | What it shows |
|---|---|---|
| `leam_taxis_testimonial_9x16.mp4` | Leam Taxis · leamingtonspa-taxis.co.uk | Desk intro, then the monitor shot. His screen is replaced with the real Google Business Profile Calls report (114 calls May–Oct 2026, September 25), and the line draws on under his finger. The selfie section uses the real site: hero, airport destinations, "For drivers / Become a driver". |
| `organic_fostering_testimonial_9x16.mp4` | Organic Fostering · organicfostering.co.uk | Interview with the site's "Cultural Matching Specialists" tick and a search bar. The blank laptop screen now shows the real Areas page, which lifts off into a card ("rebuilt our website"), plus site-fact chips and a Manchester pin. In the close-up the footage shrinks into a window over the blog and enquiry pages, then opens back up for "Honestly, it's changed everything for us." |

## What is real in the graphics

- **Website captures:** `assets/sites/*` (captured 22 Oct 2026). The OF homepage is used only for its text column, with no photos of children.
- **Leam data:** the Business Profile screenshot `assets/gsc/leamingtonspa_gbp_calls_may-oct2026.png`.
  - The chart is shown at its true aspect ratio and is never stretched.
  - The line and points are redrawn from the screenshot's own point positions. The tooltip is the screenshot's own pixels.
  - October is labelled as a part month.
- **OF site facts:** HTTPS, mobile-friendly pages, and 61 pages and 32 guides in `sitemap_20261022.xml`. "Based in Old Trafford" comes from the Areas page.
- **Logos:**
  - Organic Fostering: brand files.
  - Leam Taxis: a vector rebuild of the site logo.
  - Hulk Marketing: `assets/sites/hulkmarketing/hulk-marketing-logo.png`.

## Clean-up done on the generated footage

- **Leam shot 1:** a pint glass on the desk is cropped out with a punch-in.
- **Leam shot 2:** the made-up green screen and line are replaced with the real Business Profile chart, and his hand is composited back on top.
- **OF shot 1:** the fake lettering on the banner ("Cnar…") is painted out.
- **OF shot 3:** a small punch-in keeps the fake banner out of frame.
- **OF shot 2:** the blank laptop screen shows the real Areas page.

## Before you publish: claims that need evidence

The voices are AI-generated from the scripts. These spoken lines are claims, and UK advertising rules (CAP Code, and the DMCC Act 2024 on fake reviews) need them true and provable:

- **Leam Taxis**
  - "this is our Search Console … that's our clicks": the screen shows **Business Profile calls**, not Search Console clicks. We had no Search Console export for Leam. Send one and we swap it in, or the line should change.
  - "We're number one now for taxis in Leamington Spa": needs a dated ranking screenshot. We could not verify it (the Semrush account had no API units).
  - "airport bookings are up", "I've had to take on more drivers": need the owner's confirmation.
  - "Flat as a pancake … it just climbs": the real chart reads May 19, Jun 17, Jul 20, Aug 21 (approximate), Sept 25, then Oct 12 (part month). That is a modest rise. Confirm he is happy with the wording.
  - Confirm the 114-calls profile is Leam Taxis'.
- **Organic Fostering**
  - "They rebuilt our website, fixed the technical side, and set up our Google profile for Manchester": confirm this was Hulk's work.
  - "we're on page one for the searches that matter", "enquiries come in every week": need evidence or the owner's written confirmation.
- **Both:** each client's written OK for the AI re-creation of their likeness and words.

The videos carry an "AI re-creation" label throughout and end-card fine print ("Results vary by business"). No ranking badges, growth arrows or numbers were added beyond the real data above.

## Rebuild

```bash
cd pipeline/fostering
python3 grp_prep.py leam && python3 grp_prep.py of        # mattes, finger track, banner patches (workspace3/grp)
python3 grp_audio.py all                                   # dialogue + SFX + original music -> workspace3/audio/grp
FOSTER_FPS=24 python3 render.py grp_leam --audio ../../workspace3/audio/grp/leam_mix.wav
FOSTER_FPS=24 python3 render.py grp_of   --audio ../../workspace3/audio/grp/of_mix.wav
```

The source clips go in `workspace3/frames/leam` and `workspace3/frames/of` (721 JPGs each), registered in `workspace3/frames/manifest.json`. Captions come from `edits/asr/*.json` (faster-whisper word timings, spelling fixed in the modules).
