# RKN Accountancy: video content strategy and shoot plan

**PDF:** [`RKN_Accountancy_Video_Content_Strategy.pdf`](RKN_Accountancy_Video_Content_Strategy.pdf) (34 pages, A4)

This is a content strategy for Instagram Reels, TikTok and YouTube Shorts for RKN Accountancy (Millett House, Bury BL9 0JA). It was prepared for the shoot day on 21 October 2026 and covers:

- research: brand audit, what works for accountancy content, algorithm signals, key dates
- positioning, audiences, the four content pillars and recurring series
- 15 video concepts, one page each: hook, beats, shot list, Higgsfield AI step, caption
- 10 bonus quick-fire ideas
- a Higgsfield AI playbook (adding people and props to empty shots) with a prompt bank
- a shoot-day run sheet, B-roll list, props, kit and permissions
- posting and distribution, a hook bank and a 10-week calendar
- measurement, compliance and brand safety, quick wins and sources

## Rebuild

The source is HTML and CSS in `src/`, rendered to PDF with Chromium through Playwright:

```bash
cd src && node render.js   # writes cover.pdf + body.pdf
python3 -c "from pypdf import PdfReader, PdfWriter; w=PdfWriter(); [w.add_page(p) for f in ['cover.pdf','body.pdf'] for p in PdfReader(f).pages]; w.write('../RKN_Accountancy_Video_Content_Strategy.pdf')"
```

The body text uses Inter, which must be installed on your system. Headings use Cinzel (SIL OFL), which is in `src/fonts/`.
