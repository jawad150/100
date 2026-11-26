// Local JSON storage: settings, Brand Brain, strategy, briefs and the content planner.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

export function createStore(root) {
  const dataDir = path.join(root, "data");
  const briefsDir = path.join(dataDir, "briefs");
  fs.mkdirSync(briefsDir, { recursive: true });

  const file = (name) => path.join(dataDir, name);
  const readJSON = (p, fallback) => {
    try {
      return JSON.parse(fs.readFileSync(p, "utf8"));
    } catch {
      return fallback;
    }
  };
  const writeJSON = (p, value) => {
    const tmp = `${p}.tmp`;
    fs.writeFileSync(tmp, JSON.stringify(value, null, 2));
    fs.renameSync(tmp, p);
  };

  const DEFAULT_CONFIG = {
    apiKey: "",
    model: "claude-opus-5-5",
    depth: "standard",
    autoResearch: true,
    defaultFocus: "balanced",
    defaultSources: ["instagram", "tiktok", "youtube", "facebook"],
  };

  const safeId = (id) => String(id).replace(/[^a-zA-Z0-9_-]/g, "");

  return {
    // Settings (data/config.json is git-ignored; it holds the API key).
    getConfig() {
      const cfg = { ...DEFAULT_CONFIG, ...readJSON(file("config.json"), {}) };
      if (!cfg.apiKey && process.env.ANTHROPIC_API_KEY) cfg.apiKey = process.env.ANTHROPIC_API_KEY;
      return cfg;
    },
    keySource() {
      const saved = readJSON(file("config.json"), {});
      if (saved.apiKey) return "settings";
      if (process.env.ANTHROPIC_API_KEY) return "env";
      if (process.env.ANTHROPIC_AUTH_TOKEN) return "env";
      return null;
    },
    saveConfig(patch) {
      const current = readJSON(file("config.json"), {});
      const next = { ...DEFAULT_CONFIG, ...current, ...patch };
      writeJSON(file("config.json"), next);
      return next;
    },

    getBrand: () => readJSON(file("brand.json"), {}),
    saveBrand(brand) {
      brand.updated_at = new Date().toISOString().slice(0, 10);
      writeJSON(file("brand.json"), brand);
      return brand;
    },
    getStrategy: () => readJSON(file("strategy.json"), { sections: [] }),

    // Briefs
    newBriefId({ date, kind, focus, pinterest }) {
      const t = new Date().toISOString().slice(11, 19).replace(/:/g, "");
      return `${date}-${kind}-${focus}${pinterest ? "-pinterest" : ""}-${t}`;
    },
    saveBrief(record) {
      writeJSON(path.join(briefsDir, `${safeId(record.id)}.json`), record);
      return record;
    },
    getBrief(id) {
      return readJSON(path.join(briefsDir, `${safeId(id)}.json`), null);
    },
    deleteBrief(id) {
      const p = path.join(briefsDir, `${safeId(id)}.json`);
      if (fs.existsSync(p)) fs.unlinkSync(p);
    },
    listBriefs() {
      return fs
        .readdirSync(briefsDir)
        .filter((f) => f.endsWith(".json"))
        .map((f) => readJSON(path.join(briefsDir, f), null))
        .filter(Boolean)
        .map((b) => ({
          id: b.id,
          kind: b.kind,
          focus: b.focus,
          pinterest: b.pinterest,
          sources: b.sources,
          date: b.date,
          window: b.window,
          created_at: b.created_at,
          headline: b.brief?.headline,
          ideas: b.brief?.ideas?.length ?? 0,
          cost: b.usage?.cost ?? null,
          sample: !!b.sample,
        }))
        .sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)));
    },

    // Planner
    getPlan: () => readJSON(file("plan.json"), { items: [] }),
    addPlanItem({ idea, briefId, date }) {
      const plan = readJSON(file("plan.json"), { items: [] });
      const item = {
        id: crypto.randomUUID(),
        idea,
        brief_id: briefId ?? null,
        status: "planned",
        date: date ?? idea?.day ?? null,
        notes: "",
        added_at: new Date().toISOString(),
      };
      plan.items.push(item);
      writeJSON(file("plan.json"), plan);
      return item;
    },
    updatePlanItem(id, patch) {
      const plan = readJSON(file("plan.json"), { items: [] });
      const item = plan.items.find((i) => i.id === id);
      if (!item) return null;
      for (const k of ["status", "date", "notes"]) if (k in patch) item[k] = patch[k];
      writeJSON(file("plan.json"), plan);
      return item;
    },
    removePlanItem(id) {
      const plan = readJSON(file("plan.json"), { items: [] });
      plan.items = plan.items.filter((i) => i.id !== id);
      writeJSON(file("plan.json"), plan);
    },
  };
}
