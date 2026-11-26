// PDF rendering for daily briefs, three-day plans and the strategy, in the brand's look.
// Every block is measured before it is drawn so nothing splits, overlaps or runs off the page.
import PDFDocument from "pdfkit";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const fontkit = require("fontkit");

const C = {
  navy: "#081C26",
  teal: "#174A5C",
  cream: "#F5F2ED",
  paper: "#FBFAF7",
  card: "#F3EFE8",
  gold: "#C5A16B",
  goldLight: "#E4C99B",
  goldDark: "#8A6A3B",
  ink: "#16242B",
  muted: "#5E6A6F",
  line: "#E3DCD0",
  white: "#FFFFFF",
};

const PAGE = { w: 595.28, h: 841.89, ml: 44, mr: 44, top: 74, bottom: 56 };
const CW = PAGE.w - PAGE.ml - PAGE.mr;
const LIMIT = PAGE.h - PAGE.bottom;

const FORMAT_LABEL = { reel: "Reel", carousel: "Carousel", static: "Static post", pin: "Pin", story: "Story", short: "Short" };
const GOAL_LABEL = { lead_gen: "Lead gen", brand: "Brand", viral: "Viral", community: "Community" };
const FOCUS_LABEL = { balanced: "Balanced", leadgen: "Lead Gen", brand: "Brand & Viral" };
const PLATFORM_LABEL = { instagram: "Instagram", tiktok: "TikTok", youtube: "YouTube", facebook: "Facebook", pinterest: "Pinterest" };

const REPLACE = { "→": "›", "➜": "›", "➡": "›", "✓": "•", "✔": "•", "≈": "~", "★": "*", "—": ",", " ": " " };

function fontFiles(root) {
  const inter = (w) => path.join(root, `node_modules/@fontsource/inter/files/inter-latin-${w}-normal.woff`);
  const corm = (w, s = "normal") => path.join(root, `node_modules/@fontsource/cormorant-garamond/files/cormorant-garamond-latin-${w}-${s}.woff`);
  return {
    sans: inter(400),
    "sans-m": inter(500),
    "sans-sb": inter(600),
    "sans-b": inter(700),
    serif: corm(600),
    "serif-m": corm(500),
    "serif-i": corm(500, "italic"),
    "serif-b": corm(700),
  };
}

function createDoc(root, title) {
  const doc = new PDFDocument({
    size: "A4",
    margins: { top: PAGE.top, bottom: PAGE.bottom, left: PAGE.ml, right: PAGE.mr },
    bufferPages: true,
    autoFirstPage: false,
    info: { Title: title, Author: "Bespoke Bathroom UK · Social Studio", Creator: "Bespoke Bathroom UK Social Studio" },
  });
  const files = fontFiles(root);
  for (const [name, file] of Object.entries(files)) doc.registerFont(name, file);
  const glyphs = fontkit.openSync(files.sans);
  // Lining figures everywhere (Cormorant defaults to old-style numerals).
  const rawText = doc.text.bind(doc);
  doc.text = (...args) => {
    const last = args[args.length - 1];
    if (last && typeof last === "object" && !Array.isArray(last)) args[args.length - 1] = { features: ["lnum"], ...last };
    else args.push({ features: ["lnum"] });
    return rawText(...args);
  };
  const sanitize = (s) =>
    Array.from(String(s ?? ""))
      .map((ch) => {
        if (REPLACE[ch]) return REPLACE[ch];
        const cp = ch.codePointAt(0);
        if (cp < 32) return ch === "\n" ? ch : " ";
        return glyphs.hasGlyphForCodePoint(cp) ? ch : "";
      })
      .join("")
      .replace(/[ \t]{2,}/g, " ")
      .trim();
  return { doc, sanitize };
}

// ---------------------------------------------------------------- primitives
function makeKit(doc, sanitize, headerText) {
  let cover = false;
  doc.on("pageAdded", () => {
    if (cover) return;
    doc.save().rect(0, 0, PAGE.w, PAGE.h).fill(C.paper).restore();
    doc.font("sans-sb").fontSize(7.5).fillColor(C.goldDark);
    doc.text("BESPOKE BATHROOM UK  ·  SOCIAL STUDIO", PAGE.ml, 30, { lineBreak: false, characterSpacing: 1.4 });
    doc.font("sans").fontSize(7.5).fillColor(C.muted);
    const ht = sanitize(headerText);
    doc.text(ht, PAGE.w - PAGE.mr - doc.widthOfString(ht), 30, { lineBreak: false });
    doc.save().moveTo(PAGE.ml, 46).lineTo(PAGE.w - PAGE.mr, 46).lineWidth(0.6).strokeColor(C.goldLight).stroke().restore();
    doc.x = PAGE.ml;
    doc.y = PAGE.top;
  });

  const k = {
    doc,
    sanitize,
    setCover(v) {
      cover = v;
    },
    newPage() {
      doc.addPage();
    },
    ensure(h) {
      if (doc.y + h > LIMIT) k.newPage();
    },
    font(name, size, color) {
      doc.font(name).fontSize(size).fillColor(color ?? C.ink);
    },
    h(text, font, size, width, lineGap = 0) {
      doc.font(font).fontSize(size);
      return doc.heightOfString(sanitize(text), { width, lineGap });
    },
    write(text, { font = "sans", size = 9.5, color = C.ink, width = CW, x = PAGE.ml, lineGap = 2, gap = 6, link, align } = {}) {
      const t = sanitize(text);
      if (!t) return;
      const height = k.h(t, font, size, width, lineGap);
      if (height < LIMIT - PAGE.top) k.ensure(height);
      k.font(font, size, color);
      doc.text(t, x, doc.y, { width, lineGap, link, underline: false, align });
      doc.y += gap;
    },
    eyebrow(text, { color = C.goldDark, gap = 4, x = PAGE.ml } = {}) {
      k.font("sans-sb", 7.5, color);
      doc.text(sanitize(text).toUpperCase(), x, doc.y, { characterSpacing: 1.3, lineBreak: false });
      doc.y += 10 + gap;
    },
    sectionTitle(eyebrow, title) {
      k.ensure(80);
      doc.y += 6;
      k.eyebrow(eyebrow);
      k.write(title, { font: "serif", size: 24, color: C.navy, gap: 4, lineGap: 0 });
      doc.save().moveTo(PAGE.ml, doc.y).lineTo(PAGE.ml + 40, doc.y).lineWidth(1.4).strokeColor(C.gold).stroke().restore();
      doc.y += 14;
    },
    chips(items, { x = PAGE.ml, width = CW, fill = C.card, color = C.teal, size = 7.5 } = {}) {
      const list = items.filter(Boolean).map((s) => sanitize(s)).filter(Boolean);
      if (!list.length) return;
      k.font("sans-m", size, color);
      const ph = 6, hgt = size + 8, gapX = 5, gapY = 5;
      let cx = x, cy = doc.y;
      const rows = [];
      for (const label of list) {
        const w = doc.widthOfString(label) + ph * 2;
        if (cx + w > x + width && cx > x) {
          cx = x;
          cy += hgt + gapY;
        }
        rows.push({ label, x: cx, y: cy, w });
        cx += w + gapX;
      }
      const total = cy - doc.y + hgt;
      if (doc.y + total > LIMIT) {
        k.newPage();
        return k.chips(items, { x, width, fill, color, size });
      }
      for (const r of rows) {
        doc.save().roundedRect(r.x, r.y, r.w, hgt, hgt / 2).fill(fill).restore();
        k.font("sans-m", size, color);
        doc.text(r.label, r.x + ph, r.y + 4, { lineBreak: false });
      }
      doc.x = PAGE.ml;
      doc.y = cy + hgt + 8;
    },
    box(label, text, { bg = C.card, bar = C.gold, font = "sans", size = 9.5, color = C.ink, labelColor = C.goldDark } = {}) {
      const t = sanitize(text);
      if (!t) return;
      const pad = 10;
      const w = CW - pad * 2 - 3;
      const th = k.h(t, font, size, w, 2);
      const lh = label ? 14 : 0;
      const total = th + lh + pad * 2;
      k.ensure(Math.min(total, LIMIT - PAGE.top));
      const y0 = doc.y;
      doc.save().roundedRect(PAGE.ml, y0, CW, total, 6).fill(bg).restore();
      doc.save().rect(PAGE.ml, y0 + 6, 2.5, total - 12).fill(bar).restore();
      if (label) {
        k.font("sans-sb", 7, labelColor);
        doc.text(sanitize(label).toUpperCase(), PAGE.ml + pad + 3, y0 + pad, { characterSpacing: 1.2, lineBreak: false });
      }
      k.font(font, size, color);
      doc.text(t, PAGE.ml + pad + 3, y0 + pad + lh, { width: w, lineGap: 2 });
      doc.x = PAGE.ml;
      doc.y = y0 + total + 8;
    },
    labelled(label, text, opts = {}) {
      const t = sanitize(text);
      if (!t) return;
      const lh = 13;
      const th = k.h(t, opts.font ?? "sans", opts.size ?? 9.5, CW, 2);
      k.ensure(Math.min(lh + th + 4, 220));
      k.font("sans-sb", 7, C.goldDark);
      doc.text(sanitize(label).toUpperCase(), PAGE.ml, doc.y, { characterSpacing: 1.2, lineBreak: false });
      doc.y += lh;
      k.write(t, { gap: 8, ...opts });
    },
    bullets(items, { size = 9.5, color = C.ink, gap = 3 } = {}) {
      for (const item of items) {
        const t = sanitize(item);
        if (!t) continue;
        const w = CW - 14;
        const th = k.h(t, "sans", size, w, 2);
        k.ensure(th + gap);
        const y0 = doc.y;
        doc.save().circle(PAGE.ml + 3, y0 + size * 0.62, 1.6).fill(C.gold).restore();
        k.font("sans", size, color);
        doc.text(t, PAGE.ml + 14, y0, { width: w, lineGap: 2 });
        doc.y += gap;
      }
      doc.x = PAGE.ml;
      doc.y += 4;
    },
    // A table that keeps rows whole and repeats its header after a page break.
    table(columns, rows, { size = 8.2, headSize = 7, pad = 6, zebra = true } = {}) {
      const totalW = columns.reduce((a, c) => a + c.width, 0);
      const scale = CW / totalW;
      const cols = columns.map((c) => ({ ...c, w: c.width * scale }));
      const drawHead = () => {
        const hh = headSize + pad * 2;
        const y0 = doc.y;
        doc.save().roundedRect(PAGE.ml, y0, CW, hh, 4).fill(C.navy).restore();
        let x = PAGE.ml;
        k.font("sans-sb", headSize, C.goldLight);
        for (const c of cols) {
          doc.text(sanitize(c.title).toUpperCase(), x + pad, y0 + pad, { width: c.w - pad * 2, characterSpacing: 0.8, lineBreak: false, ellipsis: true });
          x += c.w;
        }
        doc.x = PAGE.ml;
        doc.y = y0 + hh;
      };
      const rowHeight = (row) =>
        Math.max(
          ...cols.map((c, i) => k.h(row[i] ?? "", i === 0 && c.bold ? "sans-sb" : "sans", size, c.w - pad * 2, 1.5))
        ) + pad * 2;
      k.ensure(headSize + pad * 2 + (rows[0] ? rowHeight(rows[0]) : 0));
      drawHead();
      rows.forEach((row, ri) => {
        const rh = rowHeight(row);
        if (doc.y + rh > LIMIT) {
          k.newPage();
          drawHead();
        }
        const y0 = doc.y;
        if (zebra && ri % 2 === 1) doc.save().rect(PAGE.ml, y0, CW, rh).fill(C.card).restore();
        let x = PAGE.ml;
        cols.forEach((c, i) => {
          k.font(i === 0 && c.bold ? "sans-sb" : "sans", size, i === 0 && c.bold ? C.navy : C.ink);
          doc.text(sanitize(row[i] ?? ""), x + pad, y0 + pad, { width: c.w - pad * 2, lineGap: 1.5 });
          x += c.w;
        });
        doc.save().moveTo(PAGE.ml, y0 + rh).lineTo(PAGE.ml + CW, y0 + rh).lineWidth(0.4).strokeColor(C.line).stroke().restore();
        doc.y = y0 + rh;
      });
      doc.x = PAGE.ml;
      doc.y += 10;
    },
    scoreBars(scores) {
      const keys = [
        ["overall", "Overall"],
        ["reach", "Reach"],
        ["business", "Business"],
        ["ease", "Ease"],
        ["brand_fit", "Brand fit"],
      ];
      const w = (CW - 4 * 10) / 5;
      k.ensure(30);
      const y0 = doc.y;
      keys.forEach(([key, label], i) => {
        const x = PAGE.ml + i * (w + 10);
        const v = Math.max(0, Math.min(100, Number(scores?.[key] ?? 0)));
        k.font("sans-m", 7, C.muted);
        doc.text(label.toUpperCase(), x, y0, { lineBreak: false, characterSpacing: 0.8 });
        k.font(key === "overall" ? "sans-b" : "sans-sb", 8, key === "overall" ? C.goldDark : C.navy);
        const vs = String(Math.round(v));
        doc.text(vs, x + w - doc.widthOfString(vs), y0, { lineBreak: false });
        doc.save().roundedRect(x, y0 + 12, w, 4, 2).fill(C.line).restore();
        doc.save().roundedRect(x, y0 + 12, Math.max(4, (w * v) / 100), 4, 2).fill(key === "overall" ? C.gold : C.teal).restore();
      });
      doc.y = y0 + 26;
    },
    swatches(palette) {
      const list = (palette ?? []).filter((c) => /^#?[0-9a-f]{6}$/i.test(String(c).trim())).map((c) => (c.startsWith("#") ? c : `#${c}`));
      if (!list.length) return;
      k.ensure(36);
      const y0 = doc.y;
      list.slice(0, 8).forEach((hex, i) => {
        const x = PAGE.ml + i * 62;
        doc.save().roundedRect(x, y0, 54, 18, 4).fill(hex).restore();
        doc.save().roundedRect(x, y0, 54, 18, 4).lineWidth(0.5).strokeColor(C.line).stroke().restore();
        k.font("sans", 6.5, C.muted);
        doc.text(hex.toUpperCase(), x, y0 + 21, { width: 54, align: "center", lineBreak: false });
      });
      doc.y = y0 + 36;
    },
    rule(gap = 14) {
      k.ensure(gap * 2);
      doc.y += gap / 2;
      doc.save().moveTo(PAGE.ml, doc.y).lineTo(PAGE.ml + CW, doc.y).lineWidth(0.5).strokeColor(C.line).stroke().restore();
      doc.y += gap;
    },
  };
  return k;
}

function addFooters(doc, sanitize, label) {
  const range = doc.bufferedPageRange();
  for (let i = range.start; i < range.start + range.count; i++) {
    if (i === 0) continue;
    doc.switchToPage(i);
    const bottom = doc.page.margins.bottom;
    doc.page.margins.bottom = 0;
    doc.font("sans").fontSize(7.5).fillColor(C.muted);
    doc.text(sanitize(label), PAGE.ml, PAGE.h - 34, { lineBreak: false });
    const n = `${i + 1} / ${range.count}`;
    doc.text(n, PAGE.w - PAGE.mr - doc.widthOfString(n), PAGE.h - 34, { lineBreak: false });
    doc.page.margins.bottom = bottom;
  }
}

function coverPage(k, root, { eyebrow, title, headline, summary, chips, footnote }) {
  const { doc, sanitize } = k;
  k.setCover(true);
  doc.addPage();
  doc.save().rect(0, 0, PAGE.w, PAGE.h).fill(C.navy).restore();
  // soft light pools
  const g1 = doc.radialGradient(PAGE.w * 0.85, 120, 10, PAGE.w * 0.85, 120, 320);
  g1.stop(0, C.teal, 0.55).stop(1, C.navy, 0);
  doc.save().rect(0, 0, PAGE.w, PAGE.h).fill(g1).restore();
  const g2 = doc.radialGradient(80, PAGE.h - 80, 10, 80, PAGE.h - 80, 300);
  g2.stop(0, C.goldDark, 0.35).stop(1, C.navy, 0);
  doc.save().rect(0, 0, PAGE.w, PAGE.h).fill(g2).restore();

  const logo = path.join(root, "public/assets/logo-on-dark.png");
  if (fs.existsSync(logo)) doc.image(logo, PAGE.ml, 46, { width: 170 });

  let y = 210;
  doc.font("sans-sb").fontSize(8).fillColor(C.gold);
  doc.text(sanitize(eyebrow).toUpperCase(), PAGE.ml, y, { characterSpacing: 2, lineBreak: false });
  y += 22;
  doc.font("serif").fontSize(38).fillColor(C.cream);
  doc.text(sanitize(title), PAGE.ml, y, { width: CW - 40, lineGap: -2 });
  y = doc.y + 10;
  doc.save().moveTo(PAGE.ml, y).lineTo(PAGE.ml + 56, y).lineWidth(1.5).strokeColor(C.gold).stroke().restore();
  y += 18;
  if (headline) {
    doc.font("serif-i").fontSize(20).fillColor(C.goldLight);
    doc.text(sanitize(headline), PAGE.ml, y, { width: CW - 30, lineGap: 1 });
    y = doc.y + 14;
  }
  if (summary) {
    doc.font("sans").fontSize(10).fillColor(C.cream).opacity(0.82);
    doc.text(sanitize(summary), PAGE.ml, y, { width: CW - 60, lineGap: 3 });
    doc.opacity(1);
    y = doc.y + 18;
  }
  doc.y = y;
  if (chips?.length) k.chips(chips, { fill: "#16323F", color: C.goldLight, size: 7.5 });
  if (footnote) {
    footnote(doc.y + 14);
  }
  k.setCover(false);
}

// ---------------------------------------------------------------- brief PDF
export async function renderBriefPdf(record, brand, out, root) {
  const b = record.brief;
  const isForecast = record.kind === "forecast";
  const title = isForecast ? `Three-day plan: ${record.window?.label ?? record.date}` : record.window?.label ?? record.date;
  const { doc, sanitize } = createDoc(root, `Bespoke Bathroom UK ${isForecast ? "3-day plan" : "daily brief"} ${record.date}`);
  doc.pipe(out);
  const k = makeKit(doc, sanitize, `${isForecast ? "3-day plan" : "Daily brief"} · ${record.window?.label ?? record.date}`);
  const ideasById = Object.fromEntries(b.ideas.map((i) => [i.id, i]));
  const order = [...b.ideas];

  coverPage(k, root, {
    eyebrow: `Social Studio · ${isForecast ? "Next three days" : "Daily brief"}${record.pinterest ? " · Pinterest Lab" : ""}`,
    title,
    headline: b.headline,
    summary: b.summary,
    chips: [
      `Focus: ${FOCUS_LABEL[record.focus] ?? record.focus}`,
      ...(record.sources ?? []).map((s) => PLATFORM_LABEL[s] ?? s),
      `${b.ideas.length} ideas`,
      `${b.trends.length} trends`,
    ],
    footnote: (y0) => {
      let y = Math.max(y0, 560);
      doc.font("sans-sb").fontSize(7.5).fillColor(C.gold);
      doc.text("TOP PICKS", PAGE.ml, y, { characterSpacing: 2, lineBreak: false });
      y += 18;
      (b.top_picks ?? []).slice(0, 3).forEach((id, n) => {
        const idea = ideasById[id];
        if (!idea) return;
        doc.save().roundedRect(PAGE.ml, y, CW, 48, 8).fill("#10303D").restore();
        doc.font("serif").fontSize(20).fillColor(C.gold);
        doc.text(String(n + 1).padStart(2, "0"), PAGE.ml + 14, y + 12, { lineBreak: false });
        doc.font("serif").fontSize(13.5).fillColor(C.cream);
        doc.text(sanitize(idea.title), PAGE.ml + 52, y + 10, { width: CW - 130, height: 18, ellipsis: true, lineBreak: false });
        doc.font("sans").fontSize(7.5).fillColor(C.goldLight);
        doc.text(sanitize(`${FORMAT_LABEL[idea.format] ?? idea.format} · ${GOAL_LABEL[idea.goal] ?? idea.goal} · ${idea.post_time}`), PAGE.ml + 52, y + 29, { width: CW - 130, lineBreak: false, ellipsis: true });
        doc.font("sans-b").fontSize(15).fillColor(C.gold);
        const sc = String(idea.scores?.overall ?? "");
        doc.text(sc, PAGE.ml + CW - 16 - doc.widthOfString(sc), y + 12, { lineBreak: false });
        doc.font("sans").fontSize(6.5).fillColor(C.goldLight);
        doc.text("SCORE", PAGE.ml + CW - 16 - doc.widthOfString("SCORE"), y + 31, { lineBreak: false });
        y += 56;
      });
      doc.font("sans").fontSize(7).fillColor(C.cream).opacity(0.55);
      const gen = new Date(record.created_at).toLocaleString("en-GB", { dateStyle: "long", timeStyle: "short", timeZone: "Europe/London" });
      doc.text(sanitize(`Generated ${gen}${record.sample ? " · sample brief researched for launch" : ""} · bespokebathroomsuk.co.uk`), PAGE.ml, PAGE.h - 46, { lineBreak: false });
      doc.opacity(1);
    },
  });

  // Three-day plan
  if (isForecast && b.days?.length) {
    k.newPage();
    k.sectionTitle("The plan", "Next three days at a glance");
    for (const day of b.days) {
      const ideaTitles = day.idea_ids.map((id) => ideasById[id]).filter(Boolean);
      const est = 60 + ideaTitles.length * 16 + k.h(day.prep, "sans", 9, CW, 2) + k.h(day.focus, "sans", 9.5, CW, 2);
      k.ensure(Math.min(est, 300));
      k.write(day.label, { font: "serif", size: 17, color: C.navy, gap: 4 });
      k.chips(day.moments ?? [], { fill: C.card, color: C.goldDark });
      k.labelled("Focus", day.focus);
      if (ideaTitles.length)
        k.labelled(
          "Posts",
          ideaTitles.map((i) => `${FORMAT_LABEL[i.format] ?? i.format}: ${i.title} (${i.post_time})`).join("\n")
        );
      k.box("Prep the day before", day.prep, { bg: "#EEF2F1", bar: C.teal, labelColor: C.teal, size: 9 });
      k.rule(8);
    }
  }

  // Trend radar
  k.newPage();
  k.sectionTitle("Trend radar", isForecast ? "What will be live" : "What is moving today");
  for (const t of b.trends) {
    const body = [t.what_it_is, t.why_now, t.how_we_use_it].join(" ");
    k.ensure(Math.min(90 + k.h(body, "sans", 9, CW, 2), 260));
    const y0 = doc.y;
    k.font("serif", 15.5, C.navy);
    doc.text(sanitize(t.name), PAGE.ml, y0, { width: CW - 70 });
    const after = doc.y;
    // fit badge
    doc.save().roundedRect(PAGE.ml + CW - 54, y0, 54, 30, 8).fill(C.navy).restore();
    k.font("sans-b", 12, C.gold);
    const fit = String(t.brand_fit);
    doc.text(fit, PAGE.ml + CW - 27 - doc.widthOfString(fit) / 2, y0 + 4, { lineBreak: false });
    k.font("sans", 5.8, C.goldLight);
    doc.text("BRAND FIT", PAGE.ml + CW - 27 - doc.widthOfString("BRAND FIT") / 2, y0 + 19, { lineBreak: false, characterSpacing: 0.4 });
    doc.y = Math.max(after + 4, y0 + 22);
    k.chips([...(t.platforms ?? []).map((p) => PLATFORM_LABEL[p] ?? p), t.kind, t.momentum, `Lifespan: ${t.lifespan}`], { width: CW - 64 });
    k.labelled("What it is", t.what_it_is, { size: 9 });
    k.labelled("Why now", t.why_now, { size: 9 });
    k.labelled("How we use it", t.how_we_use_it, { size: 9, color: C.teal, font: "sans-m" });
    if (t.sources?.length) {
      k.font("sans", 7.5, C.muted);
      for (const url of t.sources.slice(0, 3)) {
        k.ensure(12);
        doc.text(sanitize(url), PAGE.ml, doc.y, { width: CW, link: url, lineBreak: false, ellipsis: true });
        doc.y += 2;
      }
    }
    k.rule(10);
  }

  // Ideas
  order.forEach((idea, n) => {
    // Flow ideas: start a fresh page only when less than about half a page is left.
    if (n === 0 || doc.y > PAGE.top + (LIMIT - PAGE.top) * 0.5) k.newPage();
    else {
      doc.y += 10;
      doc.save().moveTo(PAGE.ml, doc.y).lineTo(PAGE.ml + CW, doc.y).lineWidth(1).strokeColor(C.goldLight).stroke().restore();
      doc.y += 22;
    }
    const headH = 40 + k.h(idea.title, "serif", 21, CW - 60, 0);
    k.ensure(headH + 120);
    const y0 = doc.y;
    k.font("serif-b", 30, C.gold);
    doc.text(String(n + 1).padStart(2, "0"), PAGE.ml, y0 - 4, { lineBreak: false });
    k.eyebrow(
      [
        FORMAT_LABEL[idea.format] ?? idea.format,
        GOAL_LABEL[idea.goal] ?? idea.goal,
        idea.pillar,
        (b.top_picks ?? []).includes(idea.id) ? "Top pick" : "",
      ]
        .filter(Boolean)
        .join("  ·  "),
      { x: PAGE.ml + 52, gap: 2 }
    );
    doc.y = Math.max(doc.y, y0 + 12);
    k.write(idea.title, { font: "serif", size: 21, color: C.navy, x: PAGE.ml + 52, width: CW - 52, lineGap: 0, gap: 8 });
    k.chips([
      ...(idea.platforms ?? []).map((p) => PLATFORM_LABEL[p] ?? p),
      idea.day ? new Date(`${idea.day}T12:00:00Z`).toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" }) : "",
      idea.post_time,
      `Trend: ${idea.trend}`,
    ]);
    k.scoreBars(idea.scores);
    k.box("Hook", idea.hook, { font: "serif-m", size: 15, color: C.navy, bg: C.card });
    k.labelled("The idea", idea.concept);
    k.labelled("Why it works", idea.why_it_works);

    if (idea.reel?.shots?.length) {
      k.ensure(60);
      k.eyebrow(`${FORMAT_LABEL[idea.format] ?? "Video"} script · ${idea.reel.duration_seconds} seconds`, { gap: 4 });
      k.table(
        [
          { title: "Time", width: 66, bold: true },
          { title: "Visual", width: 166 },
          { title: "On-screen text", width: 136 },
          { title: "Voiceover", width: 136 },
        ],
        idea.reel.shots.map((s) => [s.time, s.visual, s.on_screen_text, s.voiceover || "-"])
      );
      k.labelled("Audio", idea.reel.audio, { size: 9 });
      k.labelled("Edit notes", idea.reel.edit_notes, { size: 9 });
    }
    if (idea.slides?.length) {
      k.ensure(60);
      k.eyebrow(`Carousel · ${idea.slides.length} slides`, { gap: 4 });
      k.table(
        [
          { title: "#", width: 26, bold: true },
          { title: "Headline", width: 150 },
          { title: "Body", width: 180 },
          { title: "Visual", width: 150 },
        ],
        idea.slides.map((s) => [String(s.slide), s.headline, s.body, s.visual])
      );
    }
    if (idea.static_design) {
      const sd = idea.static_design;
      k.ensure(80);
      k.eyebrow("Design", { gap: 4 });
      k.box("On the image", `${sd.headline}\n${sd.subline}`, { font: "serif-m", size: 13, color: C.navy, bg: "#EEF2F1", bar: C.teal, labelColor: C.teal });
      k.labelled("Visual", sd.visual, { size: 9 });
      k.labelled("Layout", sd.layout, { size: 9 });
      k.swatches(sd.palette);
    }
    if (idea.pinterest) {
      const p = idea.pinterest;
      k.ensure(80);
      k.eyebrow("Pinterest", { gap: 4 });
      k.labelled("Pin title", p.pin_title, { font: "sans-sb" });
      k.labelled("Pin description", p.pin_description, { size: 9 });
      k.labelled("Board", p.board, { size: 9 });
      k.labelled("Alt text", p.alt_text, { size: 9 });
      k.chips(p.keywords ?? [], { fill: "#EEF2F1" });
    }
    k.box("Caption", idea.caption, { bg: C.card, size: 9.5 });
    if (idea.hashtags?.length) k.write(idea.hashtags.map((h) => (h.startsWith("#") ? h : `#${h}`)).join("  "), { size: 8.5, color: C.teal, gap: 8 });
    k.labelled("Call to action", idea.cta, { font: "sans-sb", color: C.navy });
    if (idea.lead_capture) k.labelled("Lead capture", idea.lead_capture);
    k.labelled("Production", idea.production, { size: 9 });
    if (idea.moodboard_searches?.length) {
      // One wrapped row of clickable Pinterest searches.
      k.ensure(32);
      k.font("sans-sb", 7, C.goldDark);
      doc.text("PINTEREST MOODBOARDS (CLICK TO OPEN)", PAGE.ml, doc.y, { characterSpacing: 1.2, lineBreak: false });
      doc.y += 13;
      k.font("sans-m", 8.5, C.teal);
      let cx = PAGE.ml;
      let cy = doc.y;
      for (const q of idea.moodboard_searches) {
        const label = `› ${sanitize(q)}`;
        const w = doc.widthOfString(label) + 16;
        if (cx + w > PAGE.ml + CW && cx > PAGE.ml) {
          cx = PAGE.ml;
          cy += 13;
        }
        doc.text(label, cx, cy, { link: `https://www.pinterest.co.uk/search/pins/?q=${encodeURIComponent(q)}`, lineBreak: false });
        cx += w;
      }
      doc.x = PAGE.ml;
      doc.y = cy + 16;
    }
  });

  // Watch-outs and sources
  k.newPage();
  k.sectionTitle("Before you post", "Watch-outs");
  k.bullets(b.watch_outs ?? []);
  if (b.sources?.length) {
    k.sectionTitle("Evidence", "Sources");
    for (const s of b.sources) {
      const label = sanitize(s.title || s.url);
      const h = k.h(label, "sans-m", 8.5, CW, 1) + 12;
      k.ensure(h + 4);
      k.font("sans-m", 8.5, C.navy);
      doc.text(label, PAGE.ml, doc.y, { width: CW, link: s.url });
      k.font("sans", 7.5, C.muted);
      doc.text(sanitize(s.url), PAGE.ml, doc.y, { width: CW, link: s.url, lineBreak: false, ellipsis: true });
      doc.y += 6;
    }
  }

  addFooters(doc, sanitize, `Bespoke Bathroom UK · ${isForecast ? "3-day plan" : "Daily brief"} · ${record.date}`);
  doc.end();
  await new Promise((resolve) => out.on("finish", resolve).on("close", resolve));
}

// ---------------------------------------------------------------- strategy PDF
export async function renderStrategyPdf(strategy, brand, out, root) {
  const { doc, sanitize } = createDoc(root, "Bespoke Bathroom UK social media strategy");
  doc.pipe(out);
  const k = makeKit(doc, sanitize, "Social media strategy");
  coverPage(k, root, {
    eyebrow: "Social media strategy",
    title: strategy.title ?? "Social Media Strategy",
    headline: brand.one_liner,
    summary: strategy.subtitle,
    chips: [`Updated ${strategy.updated}`, "Instagram", "TikTok", "YouTube", "Facebook", "Pinterest"],
    footnote: (y0) => {
      let y = Math.max(y0 + 10, 470);
      doc.font("sans-sb").fontSize(7.5).fillColor(C.gold);
      doc.text("CONTENTS", PAGE.ml, y, { characterSpacing: 2, lineBreak: false });
      y += 18;
      const secs = strategy.sections ?? [];
      const half = Math.ceil(secs.length / 2);
      secs.forEach((s, i) => {
        const col = i < half ? 0 : 1;
        const row = i < half ? i : i - half;
        doc.font("serif").fontSize(13).fillColor(C.cream);
        doc.text(sanitize(String(s.title).replace(/\s*\(.*\)\s*$/, "")), PAGE.ml + col * (CW / 2), y + row * 24, { width: CW / 2 - 16, height: 18, ellipsis: true });
      });
      doc.font("sans").fontSize(7).fillColor(C.cream).opacity(0.55);
      doc.text("bespokebathroomsuk.co.uk", PAGE.ml, PAGE.h - 46, { lineBreak: false });
      doc.opacity(1);
    },
  });
  k.newPage();
  for (const section of strategy.sections ?? []) {
    k.ensure(160);
    const [num, ...rest] = String(section.title).split(". ");
    k.sectionTitle(rest.length ? `Part ${num}` : "Strategy", rest.length ? rest.join(". ") : section.title);
    for (const block of section.blocks ?? []) {
      if (block.type === "p") k.write(block.text, { size: 10, lineGap: 2.5, gap: 10 });
      else if (block.type === "list") k.bullets(block.items);
      else if (block.type === "table")
        k.table(
          block.head.map((h, i) => ({ title: h, width: i === 0 ? 1.1 : block.head.length > 3 ? 1.6 : 2, bold: i === 0 })),
          block.rows
        );
      else if (block.type === "cards")
        for (const card of block.items) {
          const body = card.text + (card.meta ? `\n${card.meta}` : "");
          k.ensure(Math.min(40 + k.h(body, "sans", 9.5, CW - 26, 2), 200));
          k.write(card.title, { font: "serif", size: 14, color: C.navy, gap: 2 });
          k.write(card.text, { size: 9.5, gap: card.meta ? 2 : 10 });
          if (card.meta) k.write(card.meta, { font: "sans-sb", size: 7.5, color: C.goldDark, gap: 10 });
        }
    }
    doc.y += 6;
  }
  addFooters(doc, sanitize, "Bespoke Bathroom UK · Social media strategy");
  doc.end();
  await new Promise((resolve) => out.on("finish", resolve).on("close", resolve));
}
