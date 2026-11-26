// The research engine: phase 1 researches the live web with Claude's web search and
// web fetch tools; phase 2 turns the dossier into a structured, brand-trained brief.
import Anthropic from "@anthropic-ai/sdk";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import { BriefSchema, SingleIdeaSchema, BrandUpdateSchema } from "./schema.js";
import {
  buildSystemPrompt,
  researchTask,
  synthesisTask,
  reworkTask,
  brandLearnTask,
  brandUpdateTask,
} from "./prompts.js";

const BETAS = ["server-side-fallback-2026-07-01"];
// $ per million tokens [input, output]; web search is $10 per 1,000 searches.
const PRICES = {
  "claude-opus-5-5": [4, 20],
  "claude-sonnet-5-5": [2, 10],
};
const SEARCH_PRICE = 0.01;

export const MODELS = [
  { id: "claude-opus-5-5", label: "Opus 5.5 (best, default)" },
  { id: "claude-sonnet-5-5", label: "Sonnet 5.5 (faster, cheaper)" },
];

export class EngineError extends Error {
  constructor(message, code) {
    super(message);
    this.code = code;
  }
}

function makeClient(cfg) {
  const opts = { maxRetries: 3 };
  if (cfg.apiKey) opts.apiKey = cfg.apiKey;
  if (cfg.baseURL) opts.baseURL = cfg.baseURL;
  return new Anthropic(opts);
}

function emptyUsage() {
  return { input: 0, output: 0, cacheWrite: 0, cacheRead: 0, searches: 0, fetches: 0, cost: 0 };
}

function addUsage(total, usage, model) {
  if (!usage) return;
  const [pin, pout] = PRICES[model] ?? PRICES["claude-opus-5-5"];
  const input = usage.input_tokens ?? 0;
  const output = usage.output_tokens ?? 0;
  const cw = usage.cache_creation_input_tokens ?? 0;
  const cr = usage.cache_read_input_tokens ?? 0;
  const searches = usage.server_tool_use?.web_search_requests ?? 0;
  const fetches = usage.server_tool_use?.web_fetch_requests ?? 0;
  total.input += input;
  total.output += output;
  total.cacheWrite += cw;
  total.cacheRead += cr;
  total.searches += searches;
  total.fetches += fetches;
  total.cost +=
    (input * pin + cw * pin * 1.25 + cr * pin * 0.1 + output * pout) / 1e6 + searches * SEARCH_PRICE;
}

function translateError(err) {
  if (err instanceof EngineError) return err;
  if (err instanceof Anthropic.AuthenticationError || err instanceof Anthropic.PermissionDeniedError)
    return new EngineError("The API key was rejected. Add a valid Anthropic API key in Settings.", "auth");
  if (err instanceof Anthropic.RateLimitError)
    return new EngineError("Anthropic rate limit reached. Wait a minute and try again.", "rate_limit");
  if (err instanceof Anthropic.BadRequestError)
    return new EngineError(`The request was rejected: ${err.message}`, "bad_request");
  if (err instanceof Anthropic.APIConnectionError)
    return new EngineError("Could not reach Anthropic. Check your internet connection.", "network");
  if (err instanceof Anthropic.APIUserAbortError || err?.name === "AbortError")
    return new EngineError("Research cancelled.", "cancelled");
  if (err instanceof Anthropic.APIError)
    return new EngineError(`Anthropic API error ${err.status ?? ""}: ${err.message}`, "api");
  if (/credential|api key|apiKey|authentication/i.test(String(err?.message)))
    return new EngineError("No API key found. Add your Anthropic API key in Settings.", "auth");
  return new EngineError(err?.message || String(err), "unknown");
}

function hostOf(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
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

  // Phase 1: a web-research turn, resumed across pause_turn, streaming progress events.
  async webResearch({ client, model, effort, prompt, maxSearches, maxFetches, onEvent, signal, usage }) {
    const tools = [
      { type: "web_search_20260209", name: "web_search", max_uses: maxSearches, user_location: { type: "approximate", country: "GB", timezone: "Europe/London" } },
      { type: "web_fetch_20260209", name: "web_fetch", max_uses: maxFetches },
    ];
    const messages = [{ role: "user", content: prompt }];
    const texts = [];
    let wroteAnnounced = false;

    for (let turn = 0; turn < 6; turn++) {
      const stream = client.beta.messages.stream(
        {
          model,
          max_tokens: 32000,
          betas: BETAS,
          fallbacks: "default",
          system: [{ type: "text", text: this.system(), cache_control: { type: "ephemeral" } }],
          thinking: { type: "adaptive" },
          output_config: { effort },
          tools,
          messages,
        },
        { signal }
      );

      const blocks = {};
      for await (const ev of stream) {
        if (ev.type === "content_block_start") {
          const b = ev.content_block;
          blocks[ev.index] = { type: b.type, name: b.name, input: b.input, json: "" };
          if (b.type === "web_search_tool_result") {
            if (Array.isArray(b.content)) {
              const hosts = [...new Set(b.content.map((r) => hostOf(r.url)))].slice(0, 4);
              onEvent({ kind: "results", count: b.content.length, hosts });
            }
          } else if (b.type === "web_fetch_tool_result") {
            const url = b.content?.url;
            if (url) onEvent({ kind: "read", host: hostOf(url) });
          } else if (b.type === "text" && !wroteAnnounced) {
            wroteAnnounced = true;
            onEvent({ kind: "stage", stage: "dossier", text: "Writing the research dossier" });
          }
        } else if (ev.type === "content_block_delta" && ev.delta.type === "input_json_delta") {
          if (blocks[ev.index]) blocks[ev.index].json += ev.delta.partial_json;
        } else if (ev.type === "content_block_stop") {
          const b = blocks[ev.index];
          if (b?.type === "server_tool_use") {
            let input = b.input && Object.keys(b.input).length ? b.input : {};
            try {
              if (b.json) input = JSON.parse(b.json);
            } catch {
              /* partial input; skip the label */
            }
            if (b.name === "web_search" && input.query) onEvent({ kind: "search", query: input.query });
            else if (b.name === "web_fetch" && input.url) onEvent({ kind: "fetch", url: input.url, host: hostOf(input.url) });
            else onEvent({ kind: "filter" });
          }
        }
      }
      const msg = await stream.finalMessage();
      addUsage(usage, msg.usage, model);
      onEvent({ kind: "usage", usage: { ...usage } });
      for (const block of msg.content) if (block.type === "text") texts.push(block.text);

      if (msg.stop_reason === "pause_turn") {
        messages.push({ role: "assistant", content: msg.content });
        onEvent({ kind: "stage", stage: "research", text: "Still researching, going deeper" });
        continue;
      }
      if (msg.stop_reason === "refusal")
        throw new EngineError("The model declined this research request. Try a different focus.", "refusal");
      break;
    }
    const dossier = texts.join("\n").trim();
    if (!dossier) throw new EngineError("The research came back empty. Try again.", "empty");
    return dossier;
  }

  // Phase 2: structured output, streamed so long briefs never time out.
  async structured({ client, model, effort, prompt, schema, onEvent, signal, usage, countKey }) {
    const stream = client.beta.messages.stream(
      {
        model,
        max_tokens: 64000,
        betas: BETAS,
        fallbacks: "default",
        system: [{ type: "text", text: this.system(), cache_control: { type: "ephemeral" } }],
        thinking: { type: "adaptive" },
        output_config: { effort, format: zodOutputFormat(schema) },
        messages: [{ role: "user", content: prompt }],
      },
      { signal }
    );
    let acc = "";
    let lastCount = 0;
    for await (const ev of stream) {
      if (ev.type === "content_block_delta" && ev.delta.type === "text_delta") {
        acc += ev.delta.text;
        if (countKey) {
          const count = acc.split(`"${countKey}"`).length - 1;
          if (count !== lastCount) {
            lastCount = count;
            onEvent({ kind: "progress", count });
          }
        }
      }
    }
    const msg = await stream.finalMessage();
    addUsage(usage, msg.usage, model);
    onEvent({ kind: "usage", usage: { ...usage } });
    if (msg.stop_reason === "refusal")
      throw new EngineError("The model declined to write this brief. Try a different focus.", "refusal");
    if (msg.stop_reason === "max_tokens")
      throw new EngineError("The brief was too long and got cut off. Try again with Standard depth.", "max_tokens");
    const text = msg.content.filter((b) => b.type === "text").map((b) => b.text).join("");
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      throw new EngineError("The brief came back in an unexpected format. Try again.", "parse");
    }
    const parsed = schema.safeParse(data);
    if (!parsed.success) throw new EngineError("The brief did not match the expected structure. Try again.", "schema");
    return { data: cleanText(parsed.data), model: msg.model };
  }

  settings() {
    const cfg = this.getConfig();
    const model = cfg.model || "claude-opus-5-5";
    const deep = cfg.depth === "deep";
    return { cfg, model, deep, client: makeClient(cfg) };
  }

  async runBrief({ kind, focus, sources, pinterest, today, onEvent, signal }) {
    const { model, deep, client } = this.settings();
    const usage = emptyUsage();
    try {
      onEvent({ kind: "stage", stage: "research", text: kind === "forecast" ? "Scanning trends for the next three days" : "Scanning today's trends" });
      const dossier = await this.webResearch({
        client,
        model,
        effort: deep ? "high" : "medium",
        prompt: researchTask({ kind, focus, sources, pinterest, today, depth: deep ? "deep" : "standard" }),
        maxSearches: deep ? 35 : 18,
        maxFetches: deep ? 15 : 8,
        onEvent,
        signal,
        usage,
      });
      onEvent({ kind: "stage", stage: "ideas", text: "Turning the research into ideas for the brand" });
      const ideaCount = kind === "forecast" ? 9 : deep ? 10 : 8;
      const { data, model: served } = await this.structured({
        client,
        model,
        effort: "high",
        prompt: synthesisTask({ kind, focus, pinterest, today, dossier, ideaCount }),
        schema: BriefSchema,
        onEvent,
        signal,
        usage,
        countKey: "hook",
      });
      scoreIdeas(data, focus);
      return { brief: data, dossier, usage, model: served || model };
    } catch (err) {
      throw translateError(err);
    }
  }

  async rework({ idea, instruction, focus, signal }) {
    const { model, client } = this.settings();
    const usage = emptyUsage();
    try {
      const { data } = await this.structured({
        client,
        model,
        effort: "medium",
        prompt: reworkTask({ idea, instruction, focus }),
        schema: SingleIdeaSchema,
        onEvent: () => {},
        signal,
        usage,
      });
      return { idea: data.idea, usage };
    } catch (err) {
      throw translateError(err);
    }
  }

  async learnBrand({ website, handles, onEvent, signal }) {
    const { model, client } = this.settings();
    const usage = emptyUsage();
    try {
      onEvent({ kind: "stage", stage: "research", text: "Reading the website and social profiles" });
      const report = await this.webResearch({
        client,
        model,
        effort: "medium",
        prompt: brandLearnTask({ website, handles }),
        maxSearches: 10,
        maxFetches: 10,
        onEvent,
        signal,
        usage,
      });
      onEvent({ kind: "stage", stage: "ideas", text: "Drafting Brand Brain updates" });
      const { data } = await this.structured({
        client,
        model,
        effort: "medium",
        prompt: brandUpdateTask(report),
        schema: BrandUpdateSchema,
        onEvent,
        signal,
        usage,
      });
      return { proposal: data, report, usage };
    } catch (err) {
      throw translateError(err);
    }
  }
}
