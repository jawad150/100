// The research engine, run on the Claude plan signed in to Claude Code on this computer
// (through the Claude Agent SDK), so research uses the plan's allowance, not API credits.
// Phase 1 researches the live web with Claude Code's WebSearch and WebFetch tools;
// phase 2 turns the dossier into a structured, brand-trained brief.
import { query } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";
import { BriefSchema, BriefPlanSchema, SingleIdeaSchema, BrandUpdateSchema } from "./schema.js";
import {
  buildSystemPrompt,
  researchTask,
  dossierBlock,
  planTask,
  ideaTask,
  reworkTask,
  brandLearnTask,
  brandUpdateTask,
} from "./prompts.js";
import { SIGN_IN_COMMAND, WORK_DIR, planEnv } from "./auth.js";

export const MODELS = [
  { id: "claude-opus-5-5", label: "Opus 5.5 (best, default)" },
  { id: "claude-sonnet-5-5", label: "Sonnet 5.5 (faster, lighter on the plan)" },
];

// Credential sources that mean the run is on the Claude plan. Anything else (an API key,
// an API-key helper) would bill API credits instead, so the engine refuses to run.
const PLAN_SOURCES = new Set(["none", "oauth", "/login managed key"]);

export class EngineError extends Error {
  constructor(message, code) {
    super(message);
    this.code = code;
  }
}

function emptyUsage() {
  return { billing: "plan", input: 0, output: 0, cacheWrite: 0, cacheRead: 0, searches: 0, fetches: 0, cost: null, apiEquivalent: 0 };
}

function addUsage(total, result) {
  for (const m of Object.values(result.modelUsage ?? {})) {
    total.input += m.inputTokens ?? 0;
    total.output += m.outputTokens ?? 0;
    total.cacheWrite += m.cacheCreationInputTokens ?? 0;
    total.cacheRead += m.cacheReadInputTokens ?? 0;
  }
  total.apiEquivalent += result.total_cost_usd ?? 0;
}

// Claude Code validates output schemas as JSON Schema draft-07, so write them in that dialect
// without a $schema line (zod's default draft 2020-12 is rejected).
function jsonSchema(schema) {
  const { $schema, ...rest } = z.toJSONSchema(schema, { target: "draft-7" });
  return rest;
}

function hostOf(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

// Run fn over items with at most `limit` in flight, keeping the input order.
async function mapLimit(items, limit, fn) {
  const out = new Array(items.length);
  let next = 0;
  const worker = async () => {
    while (next < items.length) {
      const i = next++;
      out[i] = await fn(items[i]);
    }
  };
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker));
  return out;
}

// Replace dashes the brand never uses, everywhere in the output.
function cleanText(value) {
  if (typeof value === "string")
    return value
      .replace(/\s+[—–]\s+/g, ", ")
      .replace(/[—]/g, ", ")
      .replace(/\s{2,}/g, " ")
      .trim();
  if (Array.isArray(value)) return value.map(cleanText);
  if (value && typeof value === "object") {
    const out = {};
    for (const [k, v] of Object.entries(value)) out[k] = cleanText(v);
    return out;
  }
  return value;
}

function planError(text) {
  const t = String(text || "");
  if (/not logged in|please run \/login|invalid api key|authentication|oauth token|401/i.test(t))
    return new EngineError(`Claude Code is not signed in to your Claude plan. Run ${SIGN_IN_COMMAND} on this computer, then retry.`, "auth");
  if (/usage limit|rate limit|limit reached|429|overloaded/i.test(t))
    return new EngineError("Your Claude plan's usage limit has been reached for now. Wait for it to reset, then try again.", "rate_limit");
  return new EngineError(t || "Claude Code stopped unexpectedly. Try again.", "api");
}

const WEIGHTS = {
  balanced: { reach: 0.3, business: 0.3, brand_fit: 0.25, ease: 0.15 },
  leadgen: { reach: 0.2, business: 0.5, brand_fit: 0.2, ease: 0.1 },
  brand: { reach: 0.45, business: 0.1, brand_fit: 0.3, ease: 0.15 },
};

const clamp = (n) => Math.max(0, Math.min(100, Math.round(Number(n) || 0)));

export function scoreIdeas(brief, focus) {
  const w = WEIGHTS[focus] ?? WEIGHTS.balanced;
  for (const idea of brief.ideas) {
    const s = idea.scores;
    for (const k of ["reach", "business", "ease", "brand_fit"]) s[k] = clamp(s[k]);
    s.overall = clamp(s.reach * w.reach + s.business * w.business + s.brand_fit * w.brand_fit + s.ease * w.ease);
  }
  for (const t of brief.trends) t.brand_fit = clamp(t.brand_fit);
  brief.top_picks = [...brief.ideas]
    .sort((a, b) => b.scores.overall - a.scores.overall)
    .slice(0, 3)
    .map((i) => i.id);
  return brief;
}

export class ResearchEngine {
  constructor({ getConfig, getBrand, getStrategy }) {
    this.getConfig = getConfig;
    this.getBrand = getBrand;
    this.getStrategy = getStrategy;
  }

  system() {
    return buildSystemPrompt(this.getBrand(), this.getStrategy());
  }

  settings() {
    const cfg = this.getConfig();
    return { model: cfg.model || "claude-opus-5-5", deep: cfg.depth === "deep" };
  }

  // One Claude Code turn. `web` turns on WebSearch and WebFetch; `schema` asks for
  // structured output. Returns the text or the validated object, and adds to `usage`.
  async run({ model, effort, prompt, web = false, schema, maxTurns, onEvent = () => {}, signal, usage }) {
    if (signal?.aborted) throw new EngineError("Research cancelled.", "cancelled");
    const tools = web ? ["WebSearch", "WebFetch"] : [];
    const abortController = new AbortController();
    const onAbort = () => abortController.abort();
    signal?.addEventListener("abort", onAbort);
    let result = null;
    let wroteAnnounced = false;
    try {
      const q = query({
        prompt,
        options: {
          model,
          effort,
          systemPrompt: this.system(),
          tools,
          allowedTools: tools,
          permissionMode: "dontAsk",
          settingSources: [],
          strictMcpConfig: true,
          persistSession: false,
          cwd: WORK_DIR,
          env: planEnv(),
          maxTurns: maxTurns ?? (web ? 60 : 8),
          abortController,
          ...(schema ? { outputFormat: { type: "json_schema", schema: jsonSchema(schema) } } : {}),
        },
      });
      for await (const m of q) {
        if (m.type === "system" && m.subtype === "init") {
          if (!PLAN_SOURCES.has(m.apiKeySource)) {
            abortController.abort();
            throw new EngineError(`Claude Code is set to use API billing (${m.apiKeySource}), not your Claude plan. Run ${SIGN_IN_COMMAND}.`, "auth");
          }
        } else if (m.type === "assistant") {
          for (const b of m.message?.content ?? []) {
            if (b.type === "tool_use" && b.name === "WebSearch" && b.input?.query) {
              usage.searches++;
              onEvent({ kind: "search", query: b.input.query });
            } else if (b.type === "tool_use" && b.name === "WebFetch" && b.input?.url) {
              usage.fetches++;
              onEvent({ kind: "fetch", url: b.input.url, host: hostOf(b.input.url) });
            } else if (b.type === "text" && web && !wroteAnnounced && b.text?.length > 400) {
              wroteAnnounced = true;
              onEvent({ kind: "stage", stage: "dossier", text: "Writing the research dossier" });
            }
          }
        } else if (m.type === "result") {
          result = m;
        }
      }
    } catch (err) {
      if (err instanceof EngineError) throw err;
      if (signal?.aborted || err?.name === "AbortError") throw new EngineError("Research cancelled.", "cancelled");
      throw planError(err?.message);
    } finally {
      signal?.removeEventListener("abort", onAbort);
    }

    if (!result) throw new EngineError("Claude Code ended without an answer. Try again.", "empty");
    addUsage(usage, result);
    onEvent({ kind: "usage", usage: { ...usage } });
    if (result.subtype !== "success") {
      if (result.subtype === "error_max_turns") throw new EngineError("The research ran out of steps. Try again, or switch Research depth to Standard.", "max_turns");
      if (result.subtype === "error_max_structured_output_retries") throw new EngineError("The brief came back in an unexpected format. Try again.", "parse");
      throw planError((result.errors ?? []).join(" "));
    }
    if (result.is_error) throw planError(result.result);

    if (!schema) {
      const text = String(result.result ?? "").trim();
      if (!text) throw new EngineError("The research came back empty. Try again.", "empty");
      return text;
    }
    const parsed = schema.safeParse(result.structured_output);
    if (!parsed.success) throw new EngineError("The brief did not match the expected structure. Try again.", "schema");
    return cleanText(parsed.data);
  }

  async runBrief({ kind, focus, sources, pinterest, today, onEvent, signal }) {
    const { model, deep } = this.settings();
    const usage = emptyUsage();
    onEvent({ kind: "stage", stage: "research", text: kind === "forecast" ? "Scanning trends for the next three days" : "Scanning today's trends" });
    const dossier = await this.run({
      model,
      effort: deep ? "high" : "medium",
      prompt: researchTask({ kind, focus, sources, pinterest, today, depth: deep ? "deep" : "standard" }),
      web: true,
      onEvent,
      signal,
      usage,
    });

    onEvent({ kind: "stage", stage: "ideas", text: "Planning the brief from the research" });
    const ideaCount = kind === "forecast" ? 9 : deep ? 10 : 8;
    const shared = dossierBlock(dossier);
    const plan = await this.run({
      model,
      effort: "high",
      prompt: `${shared}\n\n${planTask({ kind, focus, pinterest, today, ideaCount })}`,
      schema: BriefPlanSchema,
      onEvent: (e) => e.kind === "usage" && onEvent(e),
      signal,
      usage,
    });
    if (!plan.idea_outlines.length) throw new EngineError("The plan came back with no ideas. Try again.", "empty");

    onEvent({ kind: "stage", stage: "ideas", text: `Writing ${plan.idea_outlines.length} ideas for the brand` });
    let written = 0;
    const writeIdea = async (outline) => {
      const data = await this.run({
        model,
        effort: "high",
        prompt: `${shared}\n\n${ideaTask({ focus, plan, outline })}`,
        schema: SingleIdeaSchema,
        onEvent: (e) => e.kind === "usage" && onEvent(e),
        signal,
        usage,
      });
      // The outline decides identity and placement; the full idea fills in the rest.
      const idea = { ...data.idea, id: outline.id, day: outline.day, format: outline.format };
      onEvent({ kind: "progress", count: ++written });
      return idea;
    };
    const ideas = await mapLimit(plan.idea_outlines, 3, writeIdea);

    const { idea_outlines, ...frame } = plan;
    const parsed = BriefSchema.safeParse({ ...frame, ideas });
    if (!parsed.success) throw new EngineError("The brief did not match the expected structure. Try again.", "schema");
    const brief = parsed.data;
    scoreIdeas(brief, focus);
    return { brief, dossier, usage, model };
  }

  async rework({ idea, instruction, focus, signal }) {
    const { model } = this.settings();
    const usage = emptyUsage();
    const data = await this.run({
      model,
      effort: "medium",
      prompt: reworkTask({ idea, instruction, focus }),
      schema: SingleIdeaSchema,
      signal,
      usage,
    });
    return { idea: data.idea, usage };
  }

  async learnBrand({ website, handles, onEvent, signal }) {
    const { model } = this.settings();
    const usage = emptyUsage();
    onEvent({ kind: "stage", stage: "research", text: "Reading the website and social profiles" });
    const report = await this.run({
      model,
      effort: "medium",
      prompt: brandLearnTask({ website, handles }),
      web: true,
      maxTurns: 40,
      onEvent,
      signal,
      usage,
    });
    onEvent({ kind: "stage", stage: "ideas", text: "Drafting Brand Brain updates" });
    const proposal = await this.run({
      model,
      effort: "medium",
      prompt: brandUpdateTask(report),
      schema: BrandUpdateSchema,
      onEvent,
      signal,
      usage,
    });
    return { proposal, report, usage };
  }
}
