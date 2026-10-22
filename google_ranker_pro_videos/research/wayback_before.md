# Wayback "before" captures: status report

Attempted 22 Oct 2026 (UTC 17:05 to about 17:55). British English.

## Result: Internet Archive unreachable from this sandbox, so no "before" screenshots were captured

**No `before_*.png` files exist.** Nothing below is a guess at an old design. Every domain failed the same way.

### What was tried (paced as instructed)
- **CDX API**, one domain at a time, in this order: leamingtonspa-taxis, yorkcars, goldenlinetaxiswarwick, coventryairporttaxis247, organicfostering, zentro, airporttaxis247.
  URL form: `https://web.archive.org/cdx/search/cdx?url=DOMAIN/&output=json&fl=timestamp,statuscode,digest,length&filter=statuscode:200&collapse=digest`.
  Each domain got 5 attempts (the first try plus retries after 20, 40, 80 and 160 s), with at least 8 s between domains: 35 requests over about 40 minutes.
  **All 35 failed** with `ConnectionResetError(104, 'Connection reset by peer')`.
  The agent-proxy status log puts this down to the tunnel to web.archive.org closing after about 7 s with 39 bytes received, so the archive drops the connection before any HTTP response.
  Script: `/tmp/claude-0/-home-user-100/753dbccd-034a-5c54-a3a6-3c1d83ca4518/scratchpad/wb/cdx.py`. Log: `/tmp/claude-0/-home-user-100/753dbccd-034a-5c54-a3a6-3c1d83ca4518/scratchpad/wb/cdx.log`.
- **archive.org/wayback/available** (the same organisation, a different host): returned **HTTP 429 Too Many Requests** with `x-rl: 0` on two attempts several minutes apart. The sandbox's shared egress IP (160.79.106.136) has used up the Internet Archive's rate limit. This is not something pacing on our side can fix.
- **Other archives checked once each:** archive.ph (429), Common Crawl index (connection reset), arquivo.pt CDX (403), timetravel.mementoweb.org (blocked by egress policy, 502). The UK Web Archive (webarchive.org.uk) answers, but its CDX path returns only the app shell. Its legal-deposit captures can only be viewed in a reading room anyway, so they cannot be used for screenshots.
- **Playwright through the toolbar-free `…/web/TIMESTAMPif_/https://DOMAIN/` form:** one test (leamingtonspa-taxis, `web/2023if_/`) made 5 attempts with the 20/40/80/160 s waits and got **HTTP 502 from the proxy every time**, so this route fails too. The screenshot script is ready: `/tmp/claude-0/-home-user-100/753dbccd-034a-5c54-a3a6-3c1d83ca4518/scratchpad/wb/shot.js` (usage: `node shot.js SLUG DOMAIN TIMESTAMP`). It produces `before_TIMESTAMP_desktop.png`, `before_TIMESTAMP_desktop_full.png` and `before_TIMESTAMP_mobile.png` in `assets/sites/SLUG/`, using the same 5-attempt retry schedule.

### How to finish this from a machine that can reach the archive (the user's own laptop works)
1. Open `https://web.archive.org/web/*/DOMAIN/*`, or the CDX URL above, in a normal browser.
2. Use the rebuild windows below to pick the last capture **before** each window.
3. Either send us the timestamps (we then run `shot.js`) or take the three screenshots yourself at 1440×900, full page and 390×844.

## Evidence of when each site was rebuilt (from the live sites, 22 Oct 2026)
These dates come from `wp-content/uploads/YYYY/MM` paths and footer credits in each live home page. They are clues to where to look in the archive, **not proof** of when the agency started.

| Domain | Live-site clues | Likely rebuild window (UNVERIFIED) | Where to look for "before" |
|---|---|---|---|
| leamingtonspa-taxis.co.uk | Uploads from 2017/05 to 2022/01 only. WPBakery theme. Footer "Leam Taxis 2019 ©". The Hulk case study is about Search, Maps and GBP results. | **No recent rebuild visible.** The current site is the 2017–2019 design. | A design before-and-after probably doesn't exist. Use the **rankings/calls** story (GBP 114 calls, peak 25 in Sept 2026) instead. If a Wayback capture is checked, compare 2019 against 2026 only to confirm that the design hasn't changed. |
| yorkcars.co.uk | All uploads are 2025/11–2025/12. UiCore/Elementor. Footer "Designed by Xoom Media". The Hulk case study says "a bookings-first website". | About **Nov–Dec 2025** | Last capture before about Nov 2025 (for example mid-2025). Who built it is disputed: the footer credits Xoom Media, while the Hulk portfolio lists York Cars. Confirm with the client before claiming the redesign. |
| goldenlinetaxiswarwick.co.uk | Uploads 2022/07 (1), **2023/10 (30)**, 2023/12, 2026/05 (6, new hero). Footer "Made with ❤ by Hulk Marketing Ltd". | Main build about **Oct 2023**, with a refresh about **May 2026** | Before the Oct 2023 build (if a site existed then) for "new site", or about Apr 2026 for the "hero refresh". The domain may not have existed before 2023, so check the first capture date. |
| coventryairporttaxis247.co.uk | Uploads 2022/07 (4), **2024/10–2024/11 (47)**. Sitemap shows the home page changed 3 Jun 2026 and location pages built 6–8 Jun 2026. Footer credits SMEK. | Build about **Oct–Nov 2024**, with an SEO page expansion about **Jun 2026** | The last capture before Oct 2024, and also about May 2026 (before the location pages). |
| organicfostering.co.uk | No WordPress upload paths. A custom-built site (finished reels already in this repo). The Hulk portfolio shows a "Foster Care" GoHighLevel enquiry platform. | Unknown | Pull the full CDX list. If the first capture is the current design, the site is **new** and has no "before". |
| zentro.co.uk | No WordPress upload paths. Static site with `zentro.css?v=10.25.0`. | Unknown | As above. A "new site" is likely but **unverified**. |
| airporttaxis247.co.uk | All uploads **2026/09–2026/10**. GSC avg position 72.6 (early-stage). | **Sep 2026: brand-new build** | Almost certainly no earlier design. Any earlier captures would be of a parked or previous-owner domain, which is not suitable for a before-and-after. |

## BEFORE vs NOW visual comparison
**Not possible yet**, because no BEFORE capture was retrieved. The current ("after") screenshots already exist for six sites: `/home/user/100/google_ranker_pro_videos/assets/sites/{leamingtonspa-taxis,yorkcars,goldenlinetaxiswarwick,coventryairporttaxis247,organicfostering,zentro}/now_desktop.png`, `now_desktop_full.png`, `now_mobile.png` and `now_mobile_full.png`. airporttaxis247 has no "now" capture.

## Fallbacks for video 4 (Before and after) and the case studies
1. **Ask the clients or the agency for their own records**: old-site screenshots, the theme backup or staging copy, and old Google Business Profile photos. Hulk's project records (cited on its York Cars case study as "Hulk project record") are the most likely source.
2. **Run the Wayback steps above from the user's own connection.** This takes about 10 minutes per domain, then send us the timestamps or PNGs.
3. **Use a data before-and-after instead of a design one**, which needs no archive: GSC and GBP growth already supplied (Coventry GBP interactions about 0 in May to about 32 in Aug 2026; Leam Taxis 114 calls with a Sept peak of 25). For Leam Taxis this is the honest story anyway, because its design hasn't changed.
4. Never build a "before" mock-up and present it as the client's real old site. That would be a fabricated claim.
