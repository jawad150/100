// Bespoke Bathroom UK · Social Studio
// A local web app: daily trend research, brand-trained content ideas, planner and PDF briefs.
import express from "express";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { createStore } from "./lib/store.js";
import { ResearchEngine, MODELS, EngineError, scoreIdeas } from "./lib/research.js";
import { windowDates } from "./lib/prompts.js";
import { renderBriefPdf, renderStrategyPdf } from "./lib/pdf.js";
import { PLATFORMS } from "./lib/schema.js";
import { authStatus, SIGN_IN_COMMAND } from "./lib/auth.js";

const here = path.dirname(fileURLToPath(import.meta.url));
try {
  process.loadEnvFile(path.join(here, ".env"));
} catch {
  /* no .env file: fine */
}

const PORT = Number(process.env.PORT) || 4321;
const HOST = process.env.HOST || "127.0.0.1";
const store = createStore(here);
const engine = new ResearchEngine({
  getConfig: () => store.getConfig(),
  getBrand: () => store.getBrand(),
  getStrategy: () => store.getStrategy(),
});

const londonDate = () => new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/London" }).format(new Date());

// ---------- Jobs (long research runs streamed to the browser over SSE) ----------
const jobs = new Map();

function createJob(type, meta) {
  const job = {
    id: crypto.randomUUID(),
    type,
    meta,
    status: "running",
    events: [],
    listeners: new Set(),
    result: null,
    error: null,
    controller: new AbortController(),
    started_at: new Date().toISOString(),
  };
  jobs.set(job.id, job);
  return job;
}

function emit(job, event) {
  const e = { ...event, t: Date.now() };
  job.events.push(e);
  for (const res of job.listeners) res.write(`data: ${JSON.stringify(e)}\n\n`);
}

function finish(job, status, payload) {
  job.status = status;
  if (status === "done") job.result = payload;
  else job.error = payload;
  emit(job, status === "done" ? { kind: "done", result: payload } : { kind: "error", ...payload });
  for (const res of job.listeners) res.end();
  job.listeners.clear();
  setTimeout(() => jobs.delete(job.id), 30 * 60 * 1000);
}

const runningJob = (type) => [...jobs.values()].find((j) => j.status === "running" && (!type || j.type === type));

const jobInfo = (j) => j && { id: j.id, type: j.type, meta: j.meta, status: j.status, started_at: j.started_at };

// ---------- App ----------
const app = express();
app.use(express.json({ limit: "2mb" }));
app.use(express.static(path.join(here, "public"), { extensions: ["html"] }));
app.use("/fonts/inter", express.static(path.join(here, "node_modules/@fontsource/inter/files")));
app.use("/fonts/cormorant", express.static(path.join(here, "node_modules/@fontsource/cormorant-garamond/files")));

const wrap = (fn) => (req, res) =>
  Promise.resolve(fn(req, res)).catch((err) => {
    console.error(err);
    res.status(500).json({ error: err.message || "Something went wrong" });
  });

app.get("/api/status", async (req, res) => {
  const today = londonDate();
  const briefs = store.listBriefs();
  const todays = briefs.filter((b) => b.date === today && !b.sample);
  const cfg = store.getConfig();
  const auth = await authStatus({ fresh: req.query.fresh === "1" });
  res.json({
    today,
    todayNice: windowDates("daily", today).label,
    signedIn: auth.signedIn,
    authSource: auth.source,
    plan: auth.plan,
    signInCommand: SIGN_IN_COMMAND,
    model: cfg.model,
    depth: cfg.depth,
    autoResearch: cfg.autoResearch,
    defaultFocus: cfg.defaultFocus,
    defaultSources: cfg.defaultSources,
    todayDaily: todays.find((b) => b.kind === "daily") ?? null,
    todayForecast: todays.find((b) => b.kind === "forecast") ?? null,
    autoRanToday: cfg.lastAutoResearch === today,
    latest: briefs[0] ?? null,
    job: jobInfo(runningJob()),
    models: MODELS,
  });
});

// Briefs
app.get("/api/briefs", (req, res) => res.json(store.listBriefs()));
app.get("/api/briefs/:id", (req, res) => {
  const b = store.getBrief(req.params.id);
  if (!b) return res.status(404).json({ error: "Brief not found" });
  res.json(b);
});
app.delete("/api/briefs/:id", (req, res) => {
  store.deleteBrief(req.params.id);
  res.json({ ok: true });
});
app.get(
  "/api/briefs/:id/pdf",
  wrap(async (req, res) => {
    const b = store.getBrief(req.params.id);
    if (!b) return res.status(404).json({ error: "Brief not found" });
    const name = `bespoke-bathroom-${b.kind === "forecast" ? "3-day-plan" : "daily-brief"}-${b.date}${b.pinterest ? "-pinterest" : ""}.pdf`;
    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", `attachment; filename="${name}"`);
    await renderBriefPdf(b, store.getBrand(), res, here);
  })
);

// Research jobs
app.post("/api/research", (req, res) => {
  if (runningJob("research")) return res.status(409).json({ error: "Research is already running", job: jobInfo(runningJob("research")) });
  // Auto-research runs at most once a day, even if that run fails, so reopening the
  // studio never starts another paid run on its own.
  if (req.body.auto) {
    if (store.getConfig().lastAutoResearch === londonDate()) return res.status(409).json({ error: "Auto-research already ran today", skipped: true });
    store.saveConfig({ lastAutoResearch: londonDate() });
  }
  const kind = req.body.kind === "forecast" ? "forecast" : "daily";
  const focus = ["balanced", "leadgen", "brand"].includes(req.body.focus) ? req.body.focus : "balanced";
  const pinterest = !!req.body.pinterest;
  let sources = (Array.isArray(req.body.sources) ? req.body.sources : []).filter((s) => PLATFORMS.includes(s));
  if (pinterest && !sources.includes("pinterest")) sources.push("pinterest");
  if (!pinterest) sources = sources.filter((s) => s !== "pinterest");
  if (!sources.length) sources = ["instagram", "tiktok", "youtube", "facebook"];
  const today = londonDate();
  const win = windowDates(kind, today);
  const job = createJob("research", { kind, focus, pinterest, sources, date: today, window: win.label });
  res.json({ job: jobInfo(job) });

  const t0 = Date.now();
  engine
    .runBrief({ kind, focus, sources, pinterest, today, onEvent: (e) => emit(job, e), signal: job.controller.signal })
    .then(({ brief, dossier, usage, model }) => {
      const record = store.saveBrief({
        id: store.newBriefId({ date: today, kind, focus, pinterest }),
        kind,
        focus,
        pinterest,
        sources,
        date: today,
        window: { label: win.label, dates: win.dates },
        created_at: new Date().toISOString(),
        duration_s: Math.round((Date.now() - t0) / 1000),
        model,
        usage,
        brief,
        dossier,
      });
      finish(job, "done", { briefId: record.id });
    })
    .catch((err) => {
      const e = err instanceof EngineError ? err : new EngineError(String(err?.message || err), "unknown");
      console.error(`  Research failed (${e.code}): ${e.message}`);
      finish(job, "error", { message: e.message, code: e.code });
    });
});

app.get("/api/jobs/:id/events", (req, res) => {
  const job = jobs.get(req.params.id);
  if (!job) return res.status(404).json({ error: "Job not found" });
  res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache", Connection: "keep-alive" });
  for (const e of job.events) res.write(`data: ${JSON.stringify(e)}\n\n`);
  if (job.status !== "running") return res.end();
  job.listeners.add(res);
  const ping = setInterval(() => res.write(": ping\n\n"), 15000);
  req.on("close", () => {
    clearInterval(ping);
    job.listeners.delete(res);
  });
});

app.post("/api/jobs/:id/cancel", (req, res) => {
  const job = jobs.get(req.params.id);
  if (job?.status === "running") job.controller.abort();
  res.json({ ok: true });
});

// Rework one idea in place
app.post(
  "/api/rework",
  wrap(async (req, res) => {
    const { briefId, ideaId, instruction } = req.body;
    const record = store.getBrief(briefId);
    const idx = record?.brief?.ideas?.findIndex((i) => i.id === ideaId) ?? -1;
    if (idx < 0) return res.status(404).json({ error: "Idea not found" });
    try {
      const { idea, usage } = await engine.rework({ idea: record.brief.ideas[idx], instruction: String(instruction || "Make it stronger"), focus: record.focus });
      idea.id = ideaId;
      idea.day = record.brief.ideas[idx].day;
      record.brief.ideas[idx] = idea;
      scoreIdeas(record.brief, record.focus);
      record.usage = record.usage ?? {};
      if (usage.cost != null) record.usage.cost = (record.usage.cost ?? 0) + usage.cost;
      store.saveBrief(record);
      res.json({ idea: record.brief.ideas[idx], top_picks: record.brief.top_picks });
    } catch (err) {
      console.error(`  Rework failed (${err.code ?? "unknown"}): ${err.message}`);
      res.status(err.code === "auth" ? 401 : 502).json({ error: err.message, code: err.code });
    }
  })
);

// Brand Brain
app.get("/api/brand", (req, res) => res.json(store.getBrand()));
app.put("/api/brand", (req, res) => {
  if (!req.body || typeof req.body !== "object" || !req.body.name) return res.status(400).json({ error: "Brand name is required" });
  res.json(store.saveBrand(req.body));
});
app.post("/api/brand/learn", (req, res) => {
  if (runningJob("learn")) return res.status(409).json({ error: "Already learning", job: jobInfo(runningJob("learn")) });
  const brand = store.getBrand();
  const website = String(req.body.website || brand.website || "");
  const handles = Object.values(brand.social ?? {}).filter((h) => h && !String(h).startsWith("[ADD"));
  const job = createJob("learn", { website });
  res.json({ job: jobInfo(job) });
  engine
    .learnBrand({ website, handles, onEvent: (e) => emit(job, e), signal: job.controller.signal })
    .then(({ proposal, usage }) => finish(job, "done", { proposal, usage }))
    .catch((err) => {
      console.error(`  Brand learning failed (${err.code ?? "unknown"}): ${err.message}`);
      finish(job, "error", { message: err.message, code: err.code });
    });
});

// Strategy
app.get("/api/strategy", (req, res) => res.json(store.getStrategy()));
app.get(
  "/api/strategy/pdf",
  wrap(async (req, res) => {
    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", `attachment; filename="bespoke-bathroom-social-media-strategy.pdf"`);
    await renderStrategyPdf(store.getStrategy(), store.getBrand(), res, here);
  })
);

// Planner
app.get("/api/plan", (req, res) => res.json(store.getPlan()));
app.post("/api/plan", (req, res) => {
  if (!req.body?.idea) return res.status(400).json({ error: "Idea is required" });
  res.json(store.addPlanItem({ idea: req.body.idea, briefId: req.body.briefId, date: req.body.date }));
});
app.patch("/api/plan/:id", (req, res) => {
  const item = store.updatePlanItem(req.params.id, req.body ?? {});
  if (!item) return res.status(404).json({ error: "Not found" });
  res.json(item);
});
app.delete("/api/plan/:id", (req, res) => {
  store.removePlanItem(req.params.id);
  res.json({ ok: true });
});

// Settings
app.get("/api/settings", async (req, res) => {
  const cfg = store.getConfig();
  const auth = await authStatus({ fresh: true });
  res.json({
    signedIn: auth.signedIn,
    authSource: auth.source,
    plan: auth.plan,
    signInCommand: SIGN_IN_COMMAND,
    model: cfg.model,
    depth: cfg.depth,
    autoResearch: cfg.autoResearch,
    defaultFocus: cfg.defaultFocus,
    defaultSources: cfg.defaultSources,
    models: MODELS,
  });
});
app.put("/api/settings", (req, res) => {
  const patch = {};
  const b = req.body ?? {};
  if (MODELS.some((m) => m.id === b.model)) patch.model = b.model;
  if (["standard", "deep"].includes(b.depth)) patch.depth = b.depth;
  if (typeof b.autoResearch === "boolean") patch.autoResearch = b.autoResearch;
  if (["balanced", "leadgen", "brand"].includes(b.defaultFocus)) patch.defaultFocus = b.defaultFocus;
  if (Array.isArray(b.defaultSources)) patch.defaultSources = b.defaultSources.filter((s) => PLATFORMS.includes(s));
  store.saveConfig(patch);
  res.json({ ok: true });
});

app.listen(PORT, HOST, async () => {
  const url = `http://localhost:${PORT}`;
  console.log(`\n  Bespoke Bathroom UK · Social Studio\n  Open ${url}\n`);
  if (!(await authStatus()).signedIn) console.log(`  Claude Code is not signed in to a Claude plan yet: run ${SIGN_IN_COMMAND} once on this computer.\n`);
});
