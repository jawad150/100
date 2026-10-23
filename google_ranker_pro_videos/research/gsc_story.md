# Search Console and Business Profile story notes

The source data is in `assets/gsc/gsc_data.json`, transcribed from the six PNGs in `assets/gsc/`. Every Search Console screenshot uses the "3 months" preset, which covers about 19 Jul 2026 to 18 Oct 2026. The chart axis runs from 7/19/26 to 10/15/26 and the screen says "Last update: 5.5 hours ago". Both Business Profile screenshots cover May 2026 to Oct 2026, and **October is a partial month** in both.

## 1. Strongest honest numbers, by brand

### Golden Line Taxis Warwick (goldenlinetaxiswarwick.co.uk). Strongest set.
| On-screen claim | Exact source value | Best video |
|---|---|---|
| "312 clicks from Google in 3 months" | Total clicks 312 | 2 Results walkthrough, 9 Reaction |
| "18.2K impressions in 3 months" | Total impressions 18.2K | 2, 9, 15 Founder commentary |
| "Showing for 744 different searches" | Pagination "1-25 of 744" | 15, 14 Tip (topical breadth) |
| "Our own name: position 1.8" | golden line taxis warwick: 14 clicks, 60 impr, 23.3% CTR, pos 1.8 | 3 Milestone, 8 Screen recording |
| "golden line taxis: position 2.0" | 13 clicks, 57 impr, 22.8% CTR | 3, 8 |
| "Taxi with car seat: position 1.7" | 1 click, **3 impr**, 33.3% CTR, pos 1.7 | 8 Screen recording (small volume: present it as a niche win, not as demand) |
| "Kenilworth taxis: position 6.7, page one" | 7 clicks, 291 impr, 2.4% CTR | 3 Milestone, 8 |
| "Warwick airport taxi: 13% click-through" | 6 clicks, 46 impr, 13% CTR, pos 6.1 | 8, 15 |
| "Airport taxi warwick: position 5.3" | 1 click, 64 impr, pos 5.3 | 8 ("this keyword just hit position 5", **not 3**) |
| "taxi warwick: 665 impressions, position 10.7" | 6 clicks, 665 impr, 0.9% CTR | 15 (the next target, edge of page one) |

### Coventry Airport Taxis 24/7 (coventryairporttaxis247.co.uk)
| On-screen claim | Exact source value | Best video |
|---|---|---|
| "224 clicks, 15.9K impressions in 3 months" | Totals 224 / 15.9K / 1.4% / 18.4 | 2, 9 |
| "508 searches found us" | "1-25 of 508" | 15 |
| "Coventry airport transfers: position 6.0, 10.5% CTR" | 8 clicks, 76 impr | 3, 8 |
| "Coventry airport taxi: position 7.0" | 8 clicks, 95 impr, 8.4% CTR | 3, 8 |
| "Top query: airport taxi coventry, 15 clicks" | 343 impr, 4.4% CTR, pos 13.6 | 2 |
| "Airport transfers coventry: 607 impressions" | 12 clicks, pos 22.0 | 15 (opportunity) |
| "Coventry to Birmingham airport transfers: position 4.9" | 1 click, 13 impr | 8 ("this keyword just hit position 4.9") |
| "Pre-book taxi to airport: position 2.3" | 1 click, **3 impr**, 33.3% CTR | 8 (niche, low volume) |
| "Coventry airport taxis: 26.3% click-through" | 5 clicks, 19 impr, pos 8.2 | 15 |

### Coventry Business Profile (filename says Coventry; the business name **is not visible** and must be confirmed with the user)
- **79 Business Profile interactions, May to Oct 2026** (printed on screen). The monthly values below are pixel estimates, and they sum to 79: May about 0, Jun about 6, Jul about 8, **Aug 32** (the marker sits on the 32 gridline), Sep about 20, Oct about 13 (partial month).
- Honest line: "From almost zero in May to 32 interactions in August." Do not claim the climb continued, because it fell after August. Suits video 4 Before and after (May vs Aug) and video 15.

### Leamington Spa Business Profile (likely leamingtonspa-taxis.co.uk; the business name **is not visible**)
- **114 calls made from the Business Profile, May to Oct 2026** (printed on screen). **25 calls in September 2026**, read exactly from the tooltip. Estimated months: May about 19, Jun about 17, Jul about 20, Aug about 21, Sep 25, Oct about 12 (partial).
- Honest lines: "114 phone calls straight from Google in six months" and "September: 25 calls, the best month". Suits video 9 Reaction, video 3 Milestone ("over 100 calls from Google") and video 2.
- The user says this site ranks no.1. That claim is **not shown** in these screenshots and needs its own proof (a GSC query row or a dated SERP capture).

### airporttaxis247.co.uk. Do not feature.
- 17 clicks, 4.05K impressions, 0.4% CTR, avg position 72.6, 359 queries. All of the top 25 queries have 0 clicks, at positions 44.8 to 89.8. This site is not in the user's client list, and its relationship to the agency is unverified. Use it at most as an anonymised "where a new site starts" plate, and only if the user confirms.

## 2. Matching numbers to videos
- **3 Milestone (15-20 s):** Golden Line brand term at pos 1.8; Kenilworth taxis pos 6.7 (page one); Leamington "114 calls from Google".
- **2 Results walkthrough (30-45 s):** the Golden Line totals plate (312 / 18.2K / 1.7% / 18.9), then the top-5 query rows.
- **8 Screen recording "this keyword just hit position X":** the closest real values to 3 are 2.0 (golden line taxis), 2.3 (pre book taxi to airport) and 4.9 (airport transfers coventry to birmingham). **No row sits at position 3**, so change the script to the real number.
- **9 Reaction:** the Leamington 114-calls card with the Sept 25 tooltip, or the Golden Line totals.
- **4 Before and after:** the only before/after inside one screenshot is the Coventry GBP chart (May about 0 vs Aug 32). There is no earlier Search Console period.
- **15 Founder commentary:** the opportunity rows: taxi warwick at 665 impr / pos 10.7, and airport transfers coventry at 607 impr / pos 22.0.

## 3. What the data cannot support
- **No growth percentages and no "x% more traffic".** Every Search Console screenshot shows one period with no comparison period. A growth claim needs a "Compare" export (for example the previous 3 months, or the same period last year).
- No y-axis values appear on any Search Console chart, so no daily or peak figures can be read from them. The position line visibly sits higher from about mid-August (Golden Line) and mid-September (Coventry). That is qualitative only, and the edit should not state it as a number.
- No "no.1 ranking" claim for Leamington or York Cars comes from this data. The only near-#1 positions here are brand and niche terms (1.7 to 2.3). "Position 1.8" is an **average** position, so call it "top 2", not "number 1".
- "taxi with car seat" (3 impressions) and "pre book taxi to airport" (3 impressions) are real but tiny, so do not present them as high-demand wins.
- Business Profile monthly values are pixel estimates, apart from Sept = 25 calls and the two printed totals. October is partial, so do not describe its dip as a decline.
- Bookings, revenue and calls for the Search Console sites are not shown here.
- There is no data at all for yorkcars.co.uk, zentro.co.uk or organicfostering.co.uk in these screenshots.

## 4. Crop rectangles (x, y, w, h in original pixels)
**GSC full pages** (goldenlinetaxiswarwick_gsc_3m.png, coventryairporttaxis247_gsc_3m_full.png, airporttaxis247_gsc_3m.png. All are 1366x2251 with an identical layout.)
- Totals cards (4 coloured tiles): `24, 201, 720, 110`
- Line chart with date axis: `24, 330, 1318, 240`
- Table header row: `24, 847, 1318, 57`
- Header + top 3 rows: `24, 847, 1318, 204`
- Header + top 5 rows: `24, 847, 1318, 303`
- Full 25-row table: `24, 847, 1318, 1281`
- Any single row n: `24, 904 + round((n-1)*49.1), 1318, 49`. Examples: Golden Line row 24 "taxi with car seat" `24, 2033, 1318, 49`; Coventry row 4 "coventry airport transfers" `24, 1051, 1318, 49`; row 17 "pre book taxi to airport" `24, 1690, 1318, 49`; row 14 "airport transfers coventry to birmingham" `24, 1542, 1318, 49`.
- "1-25 of N" pagination: `930, 2135, 410, 40`
- URL bar showing the property domain: `376, 8, 710, 50`

**coventryairporttaxis247_gsc_3m_chart.png** (1320x542, at a larger 1:1 scale, so it is the best plate for the Coventry totals and chart)
- Totals cards: `0, 121, 718, 110`. Chart with date axis: `20, 265, 1260, 210`. Cards + chart: `0, 121, 1300, 355`

**coventry_gbp_interactions_may-oct2026.png** (984x524)
- "79" headline + label: `40, 175, 210, 80`. Chart with month axis: `40, 275, 890, 210`. Headline + chart: `40, 175, 890, 310`. Time-period selector: `367, 58, 246, 50`

**leamingtonspa_gbp_calls_may-oct2026.png** (948x502)
- "114" headline + label: `20, 165, 240, 80`. Chart: `15, 265, 910, 210`. Headline + chart: `15, 165, 910, 310`. Sept "25" tooltip: `735, 278, 100, 55`. Time-period selector: `345, 48, 246, 50`

All the crops listed above were checked visually on test cuts in the scratchpad.

## 5. Open questions for the user
1. Which business owns each Business Profile screenshot? Neither shows the business name.
2. Can the user supply a Search Console "Compare" view (previous period) so the edit can make honest growth claims?
3. Is airporttaxis247.co.uk a client or sister site, and may it be shown?
4. Can the user supply proof of the no.1 claims for Leamington Spa Taxis and York Cars, such as a query row or a dated SERP?
