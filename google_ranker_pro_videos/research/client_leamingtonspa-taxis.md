# Client research: leamingtonspa-taxis.co.uk ("Leam Taxis")

Researched 22 Oct 2026 from the live site, plus the user-supplied Business Profile screenshot. British English. Anything not confirmed from a source is marked **UNVERIFIED**.

## 1. Business facts (from the live site)

| Item | Finding | Source |
|---|---|---|
| Trading name | **Leam Taxis** (logo, copy, footer). Site/schema name: "Leamington Spa Taxis". Google Maps embed names the Business Profile **"Leamington Spa Taxis - Airport Transfers"** | https://leamingtonspa-taxis.co.uk/ (HTML, map iframe, Rank Math schema) |
| Type | Private hire taxi / minicab firm, also airport transfers, corporate accounts, courier/parcel delivery, school contracts and "work access schemes" | /about-us/, /services/ |
| Founded | "operating in Leamington Spa, Warwick and other areas in Mid Warwickshire since 2014" | /about-us/, footer |
| Address | 51 Alexandra Road, Leamington Spa, Warwickshire CV31 2DD | /contact-us/, footer, schema |
| Phone | Shown everywhere: **07415 312 992** (mobile). BUT the schema `telephone`, the WhatsApp button and the Facebook URL use **+44 1926 555555** (landline). Inconsistent NAP: flag to the agency, and don't put either number on screen without checking with the client | home HTML |
| Email | contact@leamingtonspa-taxis.co.uk | site |
| Booking | Phone, email, WhatsApp, "Taxi App" (mentioned) and an embedded online booking widget, "Quote & Book" (app.leamingtonspa-taxis.co.uk/booking/widget), with pickup/drop-off, date/time, via, return and a green "Calculate price" button. The site says online bookings "automatically dispatch the nearest driver available" | home, /our-fleets/ |
| Hours | "7 days a week, 365 days a year"; airport transfers "24/7" | home, /services/ |
| Services | Taxi hire; airport transfers (Birmingham, Heathrow, Luton, Gatwick, Stansted, Manchester, East Midlands); meet and greet "for as little as £15"; corporate taxi; courier service (UK-wide); lost property (kept 48 hours, then handed to police); online booking; flat rate, meter or per-hour hire | home, /services/, /our-fleets/ |
| Areas | Leamington Spa (main), Warwick ("operate in both areas equally"), Kenilworth ("drivers dedicated to Kenilworth… more in numbers over the weekends"), Gaydon ("most of our corporate clients… are from JLR or Aston Martin in Gaydon"), Harbury (to/from only), Hatton Park ("usually… within 15 minutes"), Bishops Itchington, Moreton Morrell | /locations/, nav |
| Fleet | Standard/Saloon, MPV ("up to 8 passengers and luggage"), Prestige/Executive; "4, 6 and 8 seater vehicles"; "modern, air-conditioned". **No real fleet photos on the site.** The fleet images are generic stock/theme renders of yellow cabs from the WordPress "TaxiPark" theme, not UK private hire cars | /our-fleets/, theme assets |
| Drivers | "DBS checked and local residents"; "medical assessment and criminal record check every three years"; recruiting drivers (owner drivers and company drivers) | home, /our-fleets/ |
| Offers | "10% off on every 4th ride" banner; "Business car rental" banner | home (lower) |
| People named publicly | **None.** No owner, manager or driver is named. The only WordPress author is "SMEK" (username, not a person) | schema `Person` |
| Social | facebook.com/LeamTaxis01926555555, twitter.com/leam_taxis, pinterest.co.uk/leamtaxis, LinkedIn "leam-taxis-803642183", yelp.com/biz/leam-taxis-leamington-spa | footer, schema |
| Agency credit | No mention of Google Ranker Pro or Hulk on the site (searched the HTML). Relationship: user's own statement only | home HTML |
| Notable site facts | Footer reads "Leam Taxis 2019 ©". Schema homepage `dateModified` is 2024-10-17. The theme dates from 2017–2019. GTM container GTM-N3ZLQ99R is installed | HTML |

### Testimonials shown on the site (verbatim)
Source: https://leamingtonspa-taxis.co.uk/ (also repeated on /our-fleets/ and /services/). They are undated, have no surnames verified and no links to a review platform, so treat them as **UNVERIFIED site copy**. **Never** put a generated face or voice on these names.
- "We used Leam taxis for an airport taxi service to Heathrow airport, It was early hours of the morning, taxi driver called shortly before arriving, turned up on time, helped us with our heavy luggages both when picked us up and at the airport and was able to take a card payment. I can't ask for more!" — John Robertson
- "I booked Leam taxis to take me and my husband to Birmingham Airport, I have to say the driver was helpful and on time. Cheap rates for a taxi service at such an early hour (3am), Keep up Leam taxis!" — Debbie Fitzpatrick
- "After a bad experience with a different taxi firms I have hired Leam taxis to take me to work on daily basis for 3 months, they never let me down and I can confidently say I am happy with their service overall and will use them again" — Joseph White
- "Fantastic service, fetched my father from Heathrow airport. Great communication and professionalism. Will definitely be using Leam Taxis again. Thank you ?" — Ellen Kinzett
- "I pre-booked a taxi with leam taxis to take me to Coventry, driver called to confirm booking, turned up early and was driving reasonably good, Thank you leam taxis" — Khalid Nishad
- "I called leam taxis on my birthday to take us from warwick to Leamington, Prompt service, Friendly driver, good rates and a clean comfy car. Happy overall" — Pszemek Pszemek

## 2. Brand kit (for the edit only; never in the generations)
- **Logo** (/wp-content/uploads/2020/02/leam-taxis-logo.png, 181×46): a horizontal pill/lozenge with fully rounded ends, split in two. Left half is yellow (#FBCE08) with "LEAM" in a bold black geometric sans in capitals. Right half is near-black (#1A1A1A) with "TAXIS" in a thin yellow geometric sans in capitals. Under it sits the strapline "On time. Every time." in widely letter-spaced black sans. **Favicon/icon**: a yellow circle (#FFC51B) holding a black, ribbon-like looped stroke that forms a stylised "L".
- **Palette (from CSS)**:
  - primary yellow #FFC61A (136 uses in theme style.css; the logo yellow is #FBCE08)
  - near-black #1F1F1F (96 uses; the logo black is #1A1A1A)
  - light grey #F5F5F5 and #E6E6E6
  - mid grey #868686
  - accent brick red #9F340A, with #AD2727 on the mobile sticky "Call us / Email us" bar
  - green CTA #42A460 (booking widget button)
- **Fonts**: Fira Sans Condensed 700/800 for headings (uppercase), Open Sans 400/600/700 for body (Google Fonts).

## 3. Rankings: Semrush check
- **Result: not obtained.** On 22 Oct 2026 the Semrush MCP returned `no_api_units`: "The user has an active Semrush subscription, but does not have enough API units to complete this request." (trace 0252b7923c84301f037219e733b2b1e6). To get more API units, see https://www.semrush.com/mcp-access.
- So there are **no positions recorded** for: taxi leamington spa, leamington spa taxis, taxis leamington, leamington taxi, airport taxi leamington spa. Nothing is guessed. (Semrush positions are estimates in any case.)
- **"No.1" verdict: NOT VERIFIED.** The only evidence is the user's statement. Before any "No.1 on Google" line goes on screen, it needs one of:
  - a Search Console query report for this property showing average position about 1 for the named keyword, with its date range
  - a re-run Semrush pull once API units are available
  - a dated, location-stated, screen-recorded Google UK search

  Any on-screen claim must name the keyword and the date ("Position 1 for 'X', Search Console, Sept 2026"), never a bare "No.1 on Google".

## 4. Google Business Profile calls screenshot
File: assets/gsc/leamingtonspa_gbp_calls_may-oct2026.png. The screenshot shows Performance › Calls for May 2026–Oct 2026: **114** "Calls made from your Business Profile", with a peak of **25 in September 2026**. Read off the chart, the months are roughly May about 19, Jun about 17, Jul about 20, Aug about 21, Sep 25 and Oct about 12. The Oct figure is a part month, so it is not a real drop; don't present it as a decline.
**Ownership: plausible but not confirmed.** The screenshot itself shows no business name or address. The site embeds a Google Business Profile called "Leamington Spa Taxis - Airport Transfers" at about 52.277,-1.543 (Leamington Spa), and this is the only Leamington brand in the user's list. Ask the user for a screenshot that shows the profile name, or the profile share link.

## 5. Current site screenshots ("after" frames)
Saved in assets/sites/leamingtonspa-taxis/: now_desktop.png (1440×900), now_desktop_full.png (1440×5307), now_mobile.png (780×1688, which is 390×844 @2x) and now_mobile_full.png (780×18060). Script: /tmp/claude-0/-home-user-100/753dbccd-034a-5c54-a3a6-3c1d83ca4518/scratchpad/leamingtonspa-taxis_shot.js. There was no cookie banner.
**Look (desktop):**
- A thin yellow (#FFC61A) utility bar holds the phone number, "Email us" and an outlined "Get taxi online" button.
- Below it is a dark charcoal hero with a faint diagonal-hatched, desaturated city photo behind it, and the centred LEAM TAXIS logo above a white uppercase nav (Home is in yellow).
- Left of the hero is a white card: the yellow kicker "BOOK YOUR RIDE NOW", the heavy condensed black H1 "LEAMINGTON SPA TAXIS - AIRPORT TAXI TRANSFERS", then call/email lines.
- Right of the hero is the grey "QUOTE & BOOK" widget with a green "Calculate price" button.
- A row of four green-tick USPs: Instant quote, Professional drivers, Meet & greet, Free cancellation.
- Lower down: yellow line-icon service tiles, "Fleets types" cards with stock yellow cabs, a "For drivers" recruitment block, a testimonial carousel, a stock-photo "10% off every 4th ride" banner, airport logos on a yellow band, and a dark footer.

**Mobile:** a yellow top bar, the dark logo bar with a hamburger, the white hero card, then the quote widget, plus a sticky brick-red "CALL US / EMAIL US" bar along the bottom.

Overall the site works and the look is dated (a 2017 WordPress theme). Since this is the "after", it suits a *rankings/calls* story better than a *redesign* story. No "before" capture exists yet: if needed, try the Wayback Machine for a pre-engagement snapshot (dates **UNVERIFIED**).

## 6. Real-world b-roll ideas (realistic, phone/handheld-camera feel)
Shoot or generate as plain footage with **no readable signage, plates or logos**. Real footage from the client always beats generation for these:
- **Royal Leamington Spa**: the Parade (Regency terraces, white stucco), the Royal Pump Rooms, Jephson Gardens (glasshouse, River Leam), Victoria Park, the Holly Walk avenue, Clarendon Square, Leamington Spa railway station (art-deco frontage, taxi rank, Chiltern and West Midlands trains), Bath Street / Old Town, and Alexandra Road (CV31 terraced street near the base). Use generic angles only.
- **Warwick**: Warwick Castle walls from Castle Bridge / the River Avon, the market square, Smith Street, and Warwick station.
- **Kenilworth**: the castle ruins, Abbey Fields, and the town centre on a weekend night (the site claims extra weekend drivers there).
- **Gaydon**: the M40 junction 12 approach and B4100 countryside roads towards the motor industry sites. Don't show identifiable JLR/Aston Martin premises or badges without permission.
- **Airport runs**: early-morning M40 / A46 / A45 driving POV, the Birmingham Airport drop-off approach (shot generically), a driver loading heavy suitcases into a boot at 3–5 am under sodium/LED street light, and a meet-and-greet arrivals hall with a handwritten name board (blurred or fictional name).
- **Vehicles**: typical Warwick District private hire cars. Silver, white, black or grey hybrid saloons (Toyota Prius/Corolla, Skoda Octavia type), a black or silver 8-seat MPV (Mercedes Vito / Ford Galaxy type) and an executive saloon. Show the council private hire plate area only as unreadable. **NOT yellow cabs**: the site's yellow cars are theme stock. The real fleet is **UNVERIFIED**, so get photos from the client.
- **Operations**: a phone ringing or a booking ping on a mobile (07415 number style, unreadable), a driver's phone mount with a satnav, a card reader at the end of the ride, a modest office or kitchen-table dispatch setup at a terraced house. The premises at 51 Alexandra Road are **UNVERIFIED** as an office or rank, so check with the client before filming there.
- **Seasonal UK feel**: wet tarmac reflections, wipers, autumn leaves on the Parade, grey overcast daylight, real noise and grain.

## 7. Story angles the real data supports
1. **"Every call is a fare"** (videos 2, 15, case study): 114 calls from the Business Profile in May–Oct 2026, peaking at 25 in Sept 2026. Founder commentary or a labelled AI presenter explains what drove it (GBP optimisation, local pages). Overlay the real screenshot.
2. **Local pages that match how people search** (videos 8, 14): the site has a page per town (Warwick, Kenilworth, Gaydon, Hatton Park…). Tip of the week: "build one page per area you actually serve". Use only real site screens.
3. **3 am airport runs** (videos 5, 11, 12): b-roll of a real driver on an early Birmingham/Heathrow run. The site's own service copy covers it. Only use the client's driver with consent (Mode B).
4. **The owner on a decade in Mid Warwickshire, since 2014** (videos 1, 6): only if the real owner agrees to film or to have a Mode B likeness made with an approved script. No owner is named publicly, so we need their name and consent.
5. **Ranking milestone** (video 3): **only once verified** (GSC query report with a date). Until then, use the calls data instead.

## 8. Gaps and risks
- Rankings are unverified (Semrush has no API units), and the "No.1" claim must not be shown yet.
- The GBP screenshot has no business name on it, so attribution is plausible only.
- The phone numbers are inconsistent (07415 312 992 vs 01926 555555).
- No named owner or staff; consent is needed for any real-person video.
- The site testimonials are unverified, with no review-platform link. Never pair them with generated faces or voices (DMCC Act 2024 / CAP Code).
- The real fleet, livery and premises are unknown, and the site imagery is stock.
- There is no "before" site capture, and no proof on the site of the Google Ranker Pro / Hulk relationship.
- The October GBP figure is a part month.
