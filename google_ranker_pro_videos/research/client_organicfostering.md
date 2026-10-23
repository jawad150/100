# Client research: Organic Fostering (organicfostering.co.uk)

Researched 22 Oct 2026. Live site read with Node Playwright (61 sitemap URLs rendered and text-extracted, plus /areas-we-cover, /allowance-calculator, /enquire-now). Sources are cited inline.

## 1. Who they are (verified on the live site)
| Field | Value | Source |
|---|---|---|
| Legal name | Organic Fostering Ltd, company no. 14619227 | https://organicfostering.co.uk/about-us (footer on every page) |
| What it does | Ofsted-registered **independent fostering agency (IFA)**: recruits, assesses, trains and supervises foster carers. Not a taxi firm: no fleet, no drivers. | /about-us, homepage |
| Base | Beaumont House, Office 4, 455 Chester Road, Old Trafford, Manchester M16 9HA | /about-us, /areas-we-cover |
| Areas served | "Manchester and the North West" (footer strapline). The areas page deliberately lists **no towns**: "We publish an area only once we have confirmed that we are recruiting... we ask you to check your postcode with us." Blog copy mentions Greater Manchester, Liverpool and Lancashire towns in passing only. | /areas-we-cover, footer |
| Regulator | Ofsted URN 2752487. Site says "Rated Good by Ofsted · Inspected May 2025". Ofsted provider page confirms: registered 19 Mar 2024, full inspection 19 May 2025, report published 1 Jul 2025 (the grade itself was not shown in the page text we fetched, so "Good" is the site's claim; read the PDF https://files.ofsted.gov.uk/v1/file/50280933 before using the grade on screen). | homepage; https://reports.ofsted.gov.uk/provider/4/2752487 |
| Contact style | Phone **0161 241 1332**, info@organicfostering.co.uk, "Start your enquiry" form, postcode area-check form, "informal first conversation... does not commit you to applying". No online booking. | homepage, /enquire-now, /areas-we-cover |
| Strapline | NURTURE · DEVELOP · GROW | logo, homepage |
| Hero H1 | "Become a Foster Carer with Organic Fostering" | homepage |
| Trust ticks | Independent Fostering Agency · Cultural Matching Specialists · Informal First Conversation | homepage |

**Services / fostering types** (homepage carousel + pages): short-term, long-term, emergency, respite, fostering siblings, fostering teenagers; parent-and-child appears only as a blog topic (/blog/parent-and-child-fostering), not as a service page. Plus: transfer from another agency (/transfer-to-us), mandatory and additional training, supervising social worker per household, "advice outside normal hours for approved carers", carer peer contact, help with education and health needs, allowance calculator, tax guidance.

**Values** (/about-us): Acceptance, Empowerment, Excellence. "How we work": child-centred matching, trauma-aware care, professional partnership, learning throughout the journey. Route in (homepage): 01 Start a conversation, 02 Initial/home visit, 03 Apply & train, 04 Assessment, 05 Panel/approval.

**Premises / "fleet"**: an office suite at Beaumont House, a commercial building on the A56 Chester Road, Old Trafford. No vehicles. The real "product" is a carer's ordinary family home.

**People named publicly**: **none**. /about-us says only "Our service brings together social work, management, assessment, administration and family-finding experience." Ofsted page text did not list a registered manager. Do not invent names, roles or faces for this agency's staff.

**Testimonials on the site**: **none**. The site explicitly avoids them: blog "stories" pages are labelled "anonymised illustrative composites, not testimonials, identifiable case studies or promises of particular outcomes" (e.g. https://organicfostering.co.uk/blog/foster-care-stories, /blog/foster-caring-stories). There are no Google review widgets or star ratings on the site. So there is **nothing verbatim to quote** as a client voice.

## 2. Allowance figures: the repo's "verified copy" is now OUT OF DATE
The repo skill (/home/user/100/.claude/skills/organic-fostering-motion/SKILL.md) and README list 0–4 £447.60 · 5–10 £473.17 · 11–14 £515.52 · 15+ £554.02 and £23,275.20 for 52 weeks. **The live site no longer shows these.** The homepage and /allowance-calculator rate card (JSON embedded in homepage HTML, `weeklyPence`) today reads:

| Age band | Weekly per child (live, 22 Oct 2026) | Repo figure (old) |
|---|---|---|
| 0–4 | **£400.72** | £447.60 |
| 5–10 | **£430.88** | £473.17 |
| 11–14 | **£468.38** | £515.52 |
| 15+ | **£505.88** | £554.02 |
| 0–4 × 52 weeks | **£20,837.44** (shown on site) | £23,275.20 |

Live disclaimer: "Rates may vary by region and are subject to change. This estimate is for one child... an estimate does not guarantee a placement or income." Any new video must use the live figures (or none) and carry that disclaimer; the already-delivered reels 2 and anim4 now show superseded numbers. Flag to the user.

## 3. Brand kit (for the edit only; never in generations)
- **CSS tokens (:root, live)**: --brand-purple **#B7006E**, --brand-orange **#FF6411**, --purple-dark **#5B174F**, --orange-light **#FFD4BA**, --orange-ink **#933900**, --ivory **#FCF8F5**, --paper **#FFFDFB**, --ink **#321F35**, --muted **#655563**, --lavender **#F6EAF3**, --line **#E3D1DF**. Computed styles also use #A6065E (button magenta) and #4B1238 heavily.
- **Logo colours (SVG)**: magenta #A6065E, orange #F46309, leaf green #64A60C, red #CD3534, brown #855635. (Repo uses LEAF #64A60B; same green.)
- **Fonts**: **Nunito** (400 and 800 loaded; the only web font on the live site). The repo also uses Poppins and Caveat for motion work; those are our additions, not the site's.
- **Logo** (https://organicfostering.co.uk/assets/organic-fostering-final-logo-2026-09-25.svg): left, a large monogram "OF": a magenta ring "O" with a small orange heart above, inside it two orange child silhouettes holding hands (with small green leaves at their feet); the "F" is a magenta stroke whose top sprouts a green leaf. A thin vertical divider, then the wordmark stacked on two lines: "Organic" in magenta, "Fostering" in orange, rounded bold sans. Beneath, a green rule with "NURTURE • DEVELOP • GROW" in small spaced capitals (magenta letters, green dots). Wide format (2058×764). Header version on ivory.

## 4. Rankings (Semrush)
- Tried 22 Oct 2026: `mcp__Semrush__organic_research` and `mcp__Semrush__domain_overview` both returned **`no_api_units`**: "The user has an active Semrush subscription, but does not have enough API units to complete this request." (trace f4887c9f9b63d60f60aa131b0ff447bd, 98a341ac2861fb3a0c7ba8a7c2a3e2e8). More units: https://www.semrush.com/mcp-access
- So **no positions were retrieved** for: foster care agency Manchester, fostering agency Manchester, become a foster carer Manchester, independent fostering agency (Manchester). Nothing is guessed here. (Semrush positions are estimates anyway.)
- **"No.1" verdict: NOT VERIFIED.** The user made no no.1 claim for this brand, and we have no ranking data. No supplied GSC/GBP screenshot is for organicfostering.co.uk. Do not put any ranking or traffic claim for Organic Fostering on screen until the client's own Search Console export is supplied.

## 5. Safeguarding: what must never be shown
- No identifiable looked-after children: no faces, names, school uniforms with badges, school names, house numbers, street signs outside a carer's home, car number plates, or anything locating a placement.
- No real case details, even anonymised ones, presented as fact; the agency itself labels its stories as composites. Keep that.
- No generated "foster carer" or "child in care" testimonial with a face and a quote. No generated "social worker from Organic Fostering" presented as real staff (no staff are named publicly). Any presenter must be a real, consenting team member (Mode B) or a clearly labelled AI presenter.
- No guaranteed income language ("earn £20k", "guaranteed"); the site forbids it. Never "24/7" (site says "advice outside normal hours for approved carers"). Never the ad's "£2,500" (unit unknown).
- Children in generated b-roll: from behind, hands, silhouettes, out of focus, or adults only. The site's own hero photo follows this (five children from behind on a hill at sunset).
- Ofsted "Good": only with "Inspected May 2025" and after checking the report PDF.

## 6. Screenshots (current site, the "after")
Saved by /tmp/claude-0/-home-user-100/753dbccd-034a-5c54-a3a6-3c1d83ca4518/scratchpad/organicfostering_shot.js (network idle never settles on this site, so it waits for load + up to 15 s idle + 2 s; no cookie banner appeared):
- /home/user/100/google_ranker_pro_videos/assets/sites/organicfostering/now_desktop.png (1440×900)
- /home/user/100/google_ranker_pro_videos/assets/sites/organicfostering/now_desktop_full.png
- /home/user/100/google_ranker_pro_videos/assets/sites/organicfostering/now_mobile.png (390×844 @2x)
- /home/user/100/google_ranker_pro_videos/assets/sites/organicfostering/now_mobile_full.png

**Look (desktop)**: warm ivory page. Header: the full-colour logo left; a centred pill-shaped lavender nav (About fostering, Types of fostering, Support and payments, Transfer to us, About us, each with a chevron); a solid magenta "Start your enquiry ↗" button right. Hero split: left column on ivory, a small magenta eyebrow "INDEPENDENT FOSTERING AGENCY", a huge heavy Nunito aubergine H1 over three lines, grey body copy, a magenta "Start your enquiry →" button beside a magenta "Call 0161 241 1332" link, three green-ticked trust items, a hairline, "Rated Good by Ofsted · Inspected May 2025" with underlined Ofsted links, and "Am I eligible to foster? ↓". Right half: a full-bleed golden-hour photo of five children of different ethnicities, arms round each other, seen from behind looking over a town at sunset, masked by a sweeping S-curve border that gradients magenta → orange → green. **Mobile**: logo + rounded "Menu" pill, eyebrow and H1, the same sunset photo in a rounded card with a magenta curved edge, body copy, a full-width magenta enquiry button, call link and the three ticks. Clean, calm, modern, premium charity-style. (No "before" capture exists in this repo; the site was rebuilt in Sept 2026 per the logo file date 2026-09-25 and sitemap lastmod 2026-09-13. Check the Wayback Machine for a "before" if a before/after is wanted.)

## 7. Real-world b-roll ideas (authentic, Manchester, no children identifiable)
- Exterior of Beaumont House / A56 Chester Road, Old Trafford: red-brick and glass office frontage, buses (orange/yellow Bee Network buses) passing, grey drizzle or low winter sun. Shoot handheld from across the road.
- Old Trafford neighbourhood: Metrolink yellow trams at Old Trafford / Trafford Bar stops, terraced red-brick streets in Stretford and Whalley Range, wheelie bins, privet hedges (no house numbers in frame).
- Wider Manchester: Castlefield viaducts and canals, Salford Quays at dusk, the Beetham Tower skyline from Hulme, Manchester Piccadilly concourse, wet Northern Quarter pavements.
- Family-home texture (the real "premises"): a modest spare bedroom being made up (fresh duvet, a lamp, a small plant), a kitchen table with a mug and a school-run lunchbox, coats on hooks, wellies by the door, a fridge with drawings (no names), a car boot with a child seat shot from inside (no plate).
- Adult-only work scenes: an assessing social worker's notebook and lanyard (no name) on a carer's kitchen table, two adults talking over tea, a phone call by a window, a laptop open on a training slide (blurred), a small group training session in a plain office room.
- Children only from behind or as hands: a hand-in-hand walk to a primary school gate (gate unbranded), a kicked football in a park (Longford Park, Stretford), bikes in a hallway, a homework pencil.
- UK texture cues: British plug sockets, radiators under windows, UPVC windows with condensation, a kettle, a Greggs paper bag, overcast flat light, Manchester rain on glass.

## 8. Story angles the real data supports
No GSC, GBP or ranking data exists for this brand in the supplied set, so results-led videos (2, 3, 4-traffic, 8, 9, 15) **cannot** be made honestly for Organic Fostering yet. Angles that can:
1. **Before/after website rebuild (video 4, "old site vs new")**: the live site is a fresh rebuild (logo file dated 25 Sept 2026, sitemap lastmod 13 Sept 2026): clear allowance calculator, postcode area-check, plain-English FAQ, 61 URLs in the sitemap including 32 blog guides plus a blog index. Use our new screenshots as the "after"; source a "before" from the Wayback Machine. Claim only what is visible (pages, structure), not rankings.
2. **Content engine / topical authority (video 15 founder commentary, or 11 behind the scenes)**: a real, countable fact: 32 blog guides in the sitemap targeting carer questions ("can you work and be a foster parent", "do you get paid to foster a child", "fostering assessment questions"), each written with GOV.UK/HMRC citations and safeguarding-safe composites instead of fake testimonials. Good "how we do SEO for regulated sectors" story. Results only once the client's GSC is supplied.
3. **Ethical marketing in a safeguarding sector (video 14 SEO tip / 13 founder)**: "we don't fake testimonials" — mirror the agency's own composite-story policy and the DMCC Act; tip: answer the real questions searchers ask (allowance, eligibility, single carers) instead of buying reviews.
4. **Conversion features (video 8 screen recording, no ranking claim)**: phone-filmed scroll of the live allowance calculator and the postcode area checker; voiceover explains why they reduce friction. Uses only live, verifiable UI.
5. **Existing footage reuse**: the repo already holds 19 client Drive clips ("fostering") and five finished motion pieces (README). These can intercut with any new generated b-roll, but the old £447.60 figures in reel2/anim4 must not be reused.

## 9. Gaps and risks
- Semrush: no API units; no rankings retrieved. Need the client's GSC export to make any performance claim.
- No public staff names or testimonials; client-voice videos (1, 2, 3, 5, 6, 9) need a consenting real carer/staff member on camera, and real carers may themselves need anonymity for the children's safety.
- Repo allowance copy is outdated (see section 2).
- Ofsted "Good" grade not independently confirmed from the report PDF.
- Hero photo on the site may be stock or AI (it has a polished look); do not reuse it as "real" footage in our edits without checking its source.
