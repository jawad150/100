# Client research: Zentro (zentro.co.uk)

Researched 22 Oct 2026 from the live site (pages fetched: `/`, `/about-us`, `/contact-us`, `/faqs`, `/repair-services`, `/laptop-repair`, `/mobile-repair`, `/business-it-support`, `/terms-and-conditions`, `/privacy-policy`, plus `zentro.css?v=10.25.0`, `zentro-logo.png`, `og-image.jpg`).

**Important framing: Zentro is NOT a taxi firm.** Unlike the other brands in the list, it is a technology business: laptop and mobile repair, a device/accessory marketplace, and Business IT Support for offices.

## 1. What Zentro is

| Item | Finding | Source |
|---|---|---|
| Business name | Zentro | site-wide; schema.org `Organization` on https://zentro.co.uk/ |
| What it does | "Laptop & Mobile Repair, Device Sales & Business IT Support" (page title). Three routes: Laptop & Mobile Repair, Marketplace, Business IT | https://zentro.co.uk/ , https://zentro.co.uk/about-us |
| Base location | **No street address published anywhere on the site.** Phone 0161 564 8313 is a Greater Manchester (0161) number, so a Manchester base is *likely but unverified*. Schema `areaServed` = "United Kingdom"; contact page says "Service area: United Kingdom" | https://zentro.co.uk/contact-us |
| Areas served | UK-wide (courier, drop-off, collection "subject to service availability and location") | https://zentro.co.uk/faqs |
| Phone / booking style | Online booking journey (device → brand → range → exact model → repair service), "Track My Repair" by reference, live chat, phone 0161 564 8313, email support@zentro.co.uk. Business IT: "Request IT Support" / "Book IT Enquiry" form, "Within 1 business hour" response, "Remote-first helpdesk, onsite when required" | home, /book-repair, /business-it-support |
| Hours | Footer: "Mon – Sun: 9AM – 7PM" (and schema 09:00–19:00 daily). Contact page body says "Mon–Fri · 9AM–7PM" (**inconsistent**) | footer; /contact-us |
| Email | Footer/schema: support@zentro.co.uk; contact page body: support@**zentro.com** (**inconsistent, probably a typo**) | /contact-us |
| People named publicly | **None.** No owner, manager or technician named on any page fetched. No company number or registered address in Terms/Privacy | all pages |
| Agency credit | No "Hulk" / Google Ranker Pro credit found in the site HTML | grep of all fetched pages |

### Services (from the site)
- **Laptop repair** (10 brands): Apple (MacBook), Dell, HP, Lenovo, ASUS, Acer, Microsoft Surface, Samsung, MSI, Razer. Screen, battery, motherboard, diagnostics, upgrades.
- **Mobile repair**: Apple (iPhone), Samsung (Galaxy), Google (Pixel): screen, battery, camera, charging.
- **Marketplace**: new and refurbished laptops, smartphones, desktops; chargers & power, storage & memory (SSD/NVMe/RAM), keyboards & mice, docks & hubs, screens & batteries. Condition grades (Fair/Good/Excellent). Featured prices on home page, e.g. HP EliteBook 840 G6 £185, HP EliteBook 840 G11 £350, Apple iPhone 13 Pro £300, iPhone 17 Pro Max £900, Dell Precision 3561 £300.
- **Business IT Support (offices only)**: Managed IT Support, Network & Wi-Fi Setup, Device Management, Cybersecurity Protection, Backup & Recovery, Software Support, Microsoft 365 & Cloud, IT Projects & Migrations, Support Plans, Track IT Request.

### Claims made on the site (all self-declared, none independently sourced)
- "90-Day Warranty On All Repairs"; "Genuine Parts"; "Certified Technicians"; "Quick Turnaround: Most Repairs in 24–48h"; "In-house Repair Experience".
- "**5,000+ Happy Customers ★★★★★ 4.8/5 (2,560+ Reviews)**": no review platform named or linked. **Unverified. Do not reuse in any video.**
- Business IT: "Within 1 business hour" response.

### Testimonials shown on the site (verbatim, https://zentro.co.uk/ "What Our Customers Say" carousel)
1. "Quick pickup, fair pricing, and my laptop works like new. Highly recommend Zentro!" (Aman Sharma, London)
2. "Zentro replaced my phone battery quickly and kept me updated throughout. Very easy service." (Priya Mehta, Manchester)
3. "Bought a mobile from Zentro and the ordering process was clear, quick and straightforward." (Rahul Patel, Birmingham)
4. "Our office IT setup was seamless. Reliable team and outstanding support." (Rhea Bansal, Leeds)
5. "Straightforward repair process and clear communication from start to finish." (Amir Khan, London)
6. "The replacement battery works perfectly and the turnaround was quick." (Sarah Jones, Bristol)
7. "Very useful business IT consultation and no confusing jargon." (Daniel Wright, Reading)
8. "Ordered an SSD upgrade and the service was excellent." (Hannah Green, Oxford)
9. "Ordering was straightforward and the condition description matched what arrived. Packaging was secure and delivery updates were clear." (Daniel M., Manchester)
10. "The product page made it easy to compare the options and I knew exactly what was included before checkout." (Sarah K., Birmingham)
11. "Very clean buying process. The device was well prepared and the warranty information was easy to understand." (James R., Leeds)
12. "Good communication, quick checkout and the product arrived in the condition I selected." (Aisha N., London)
13. "The images and specifications were useful and support answered my compatibility question before I ordered." (Oliver T., Bristol)
14. "I liked being able to choose the cosmetic grade rather than guessing what refurbished meant." (Maya P., Nottingham)

**Risk flag:** these have no source platform, no dates, and read like template/placeholder copy (spread across many cities for a business with no address). Treat as **unverified**. Never voice them with a generated face, never put them on screen in our videos. Worth raising with the client privately: under the DMCC Act 2024 (fake reviews) and CAP Code, unverifiable reviews and the "4.8/5 (2,560+ reviews)" badge are a compliance risk for Zentro itself.

## 2. Brand kit (for the edit only, never in generations)

- **Palette (from `zentro.css` tokens):**
  - Accent orange `#FF5A00` (`--accent`, the most-used colour, 93 uses), dark orange `#DF4E00` (`--accent-dark`), accent tint `#FFF4ED` (`--accent-soft`), warm tints `#FFF0E7`, `#FFF8F4`.
  - Ink `#15171B` (`--ink`), alt ink `#18212A`, muted grey `#6E737B` / `#626A72`, lines `#E7E8EB`, soft backgrounds `#F8F9FA` / `#EDF0F2`, white `#FFFFFF`.
  - Minor: red `#E11D48` (`--zw-red`, alerts).
- **Fonts:** Inter (stack `Inter, "Segoe UI", Arial, sans-serif`). Headlines are heavy Inter (bold/extra-bold, tight tracking); body regular Inter. No webfont file is loaded by the site (relies on locally installed Inter), so use Inter from Google Fonts in the edit.
- **Logo:** black-on-white monogram plus wordmark. The mark is a square-ish geometric "Z" built from thick black strokes: a top horizontal bar, a diagonal down to the lower-left, a bottom-left chevron, with a second diagonal and a tall vertical bar on the right that together read as an "N" interlocked with the Z (a "ZN"/"Z" monogram with an arrow-like inner chevron). Below it, the wordmark "ZENTRO" in wide-tracked, thin geometric sans-serif capitals; the "N" has a small sliced/broken diagonal. Monochrome black only; the orange is a UI accent, not part of the logo. Files: https://zentro.co.uk/assets/images/zentro-logo.png (364×291 PNG, white background, no transparency), OG card https://zentro.co.uk/assets/images/og-image.jpg (1200×630, tagline "Laptop & Mobile Repair · Device Sales · Business IT Support").

## 3. Rankings (Semrush, database "uk")

Attempted 22 Oct 2026: `organic_research` and `domain_overview` both returned **`no_api_units`**: the Semrush account has an active subscription but not enough API units to complete the request (more units: https://www.semrush.com/mcp-access). **No ranking data was retrieved.**

Core keywords derived from the site (to check once units are available): `laptop repair manchester`, `laptop repair`, `macbook repair manchester`, `iphone screen repair manchester`, `mobile phone repair manchester`, `refurbished laptops uk`, `hp elitebook 840 g6 refurbished`, `it support manchester`, `managed it support manchester`, `business it support`, `zentro` (brand).

**Verdict:** the user made **no "no.1" claim for Zentro**, and no ranking claim of any kind can be verified at present. No Search Console or Business Profile screenshot for Zentro was supplied either. **Zero numbers for Zentro may go on screen until real data arrives.**

## 4. Screenshots of the current site (the "after")

Saved with Playwright on 22 Oct 2026 (`/tmp/claude-0/-home-user-100/753dbccd-034a-5c54-a3a6-3c1d83ca4518/scratchpad/zentro_shot.js`); no cookie banner appeared.
- `/home/user/100/google_ranker_pro_videos/assets/sites/zentro/now_desktop.png` (1440×900)
- `/home/user/100/google_ranker_pro_videos/assets/sites/zentro/now_desktop_full.png` (1440×4884)
- `/home/user/100/google_ranker_pro_videos/assets/sites/zentro/now_mobile.png` (390×844 @2x)
- `/home/user/100/google_ranker_pro_videos/assets/sites/zentro/now_mobile_full.png` (390×8596 @2x)

**Look (desktop above the fold):** clean, bright, Apple-store-style ecommerce layout on white. A thin grey trust strip on top (In-house Repair Experience · 90-Day Warranty · Genuine Parts · Secure Service · Data Protection · Expert Technicians | Live Chat | 0161 564 8313). Header: small black ZN monogram + "ZENTRO" at left, nav (Repairing Services, Business IT Support, Marketplace, About Us, Contact, FAQs), account/wishlist/cart icons and an orange "Book a Repair" button. Hero: orange eyebrow "PROFESSIONAL. RELIABLE. TRUSTED.", huge heavy black headline "Expert Laptop & Mobile Repair," with "You Can Trust." in orange, a subline, four orange-ticked trust points, orange "Book a Repair" + outlined "Track My Repair" buttons, and avatar row "5,000+ Happy Customers ★ 4.8/5 (2,560+ Reviews)". Right side: rendered silver laptop showing the Zentro logo on a soft wave wallpaper beside a graphite iPhone. Below: "One Place for Repairs, Devices & Business IT". Modern, polished, SaaS-like; strong orange/black contrast.

No "before" version is on file: if the agency rebuilt the site, ask the user for the old site screenshots or a Wayback Machine capture date.

## 5. Real-world b-roll ideas (Mode A: no real identities; authentic UK repair-bench look)

All must read as handheld phone or real-camera footage: natural mixed light, real dust and fingerprints on screens, worn ESD mats, imperfect cable clutter. No logos or text in the generations (Zentro branding goes in the edit).
- Close-up repair bench: anti-static mat, magnetic screw tray, iFixit-style spudgers, pentalobe screwdriver on a MacBook base, heat pad lifting an iPhone screen, suction cup, tweezers placing a ribbon connector, a swollen laptop battery beside a new one.
- Microscope / loupe shot of a motherboard; soldering station with a thin wisp of smoke; multimeter probes.
- Technician's hands (no face) running a diagnostics screen on a ThinkPad or EliteBook; a phone booting to its lock screen after a screen swap.
- Refurbished stock shelf: rows of used HP EliteBooks and Dell Latitudes with grading stickers (blank), padded jiffy bags, a courier handing over a box at a door (generic, no livery).
- Business IT: an office comms cupboard with a patch panel and a Ubiquiti-style ceiling Wi-Fi access point, a laptop being set up for a new starter at a desk, someone tapping an MFA prompt on a phone.
- Manchester street context (*only if the Manchester base is confirmed*): rain on a Northern Quarter street, a tram passing on Market Street or Piccadilly Gardens, red-brick mill buildings in Ancoats, a city-centre office window at dusk. Otherwise keep b-roll location-neutral (generic UK high street, terraced street, office interior).
- Phone-filmed "customer" moments without faces: hands receiving a repaired phone in a padded envelope at a kitchen table, a cracked screen before / clean screen after.

## 6. Story angles the real data supports (and what is missing)

There is **no Zentro performance data on file** (no Search Console, no Business Profile, no Semrush). So every angle below is either data-free or waits on the client's numbers.
1. **"Three businesses, one site" (Founder commentary, #15, or BTS #11):** the agency's real work you can show on screen is the site itself: a structured repair journey (brand → model → service), a marketplace, and a separate Business IT section with service pages. Use the screenshots as the "after". Strictly no traffic claims until Zentro's Search Console is supplied.
2. **SEO tip of the week (#14): "Build a page for every model people search for."** Zentro's brand/model repair pages (e.g. /laptop-repair/dell, /mobile-repair/apple) are a live example of model-level landing pages. Tip is generic and true; no numbers required.
3. **SEO tip (#14): "Fake-looking reviews can cost you."** Use Zentro *anonymously or not at all*: an educational tip on DMCC Act 2024 review rules. Only with the client's knowledge; better as a private recommendation than public content.
4. **Before and after (#4) / Results walkthrough (#2):** possible only once the user supplies (a) the old site screenshots and (b) Zentro Search Console / GBP exports. Then: old vs new site, plus real clicks/impressions growth.
5. **Behind the scenes (#11) / Day in the life (#12):** an agency team member building out Zentro's model-level repair pages or schema, filmed over the shoulder (screen content added in the edit from the real screenshots).

## 7. Gaps and risks
- Semrush returned `no_api_units`: no ranking data. No GSC/GBP data for Zentro supplied.
- No address, no named people, no company number on the site; base location only inferred from the 0161 number.
- Site inconsistencies: email zentro.com vs zentro.co.uk; hours Mon–Fri vs Mon–Sun.
- On-site testimonials and the "5,000+ customers / 4.8/5 (2,560+ reviews)" badge are unsourced and look like placeholder copy: never reuse them, never attach them to any face.
- Hero device imagery on the site is a render: do not imitate it in generations (the user wants real-camera footage).
- Zentro is a tech repair/IT business, so the taxi-style b-roll used for the other clients does not apply.
- Relationship to Hulk Marketing / Google Ranker Pro not stated on the Zentro site (no footer credit).
