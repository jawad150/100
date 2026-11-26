// Structured-output schemas for the research engine.
// Kept free of min/max constraints so they compile for Claude structured outputs.
import { z } from "zod";

export const PLATFORMS = ["instagram", "tiktok", "youtube", "facebook", "pinterest"];
export const FORMATS = ["reel", "carousel", "static", "pin", "story", "short"];
export const GOALS = ["lead_gen", "brand", "viral", "community"];

const Platform = z.enum(PLATFORMS);

export const TrendSchema = z.object({
  name: z.string().describe("Short trend name, e.g. 'Quiet luxury bathroom reveal'"),
  platforms: z.array(Platform),
  kind: z.enum(["audio", "format", "meme", "topic", "aesthetic", "moment", "search"]),
  what_it_is: z.string().describe("One or two sentences: what the trend looks like in practice"),
  why_now: z.string().describe("Evidence of momentum right now, with dates where known"),
  how_we_use_it: z.string().describe("How Bespoke Bathroom UK should adapt it, in one or two sentences"),
  brand_fit: z.number().describe("0-100: how well it fits a premium bathroom design, supply and fit brand"),
  momentum: z.enum(["rising", "peaking", "steady", "fading"]),
  lifespan: z.enum(["hours", "days", "weeks", "evergreen"]),
  sources: z.array(z.string()).describe("URLs that evidence the trend"),
});

const ShotSchema = z.object({
  time: z.string().describe("Timecode range, e.g. '0:00-0:02'"),
  visual: z.string(),
  on_screen_text: z.string(),
  voiceover: z.string().describe("Spoken line, or empty string if none"),
});

const SlideSchema = z.object({
  slide: z.number(),
  headline: z.string(),
  body: z.string(),
  visual: z.string().describe("What the slide shows: photo, render, layout, colour"),
});

export const IdeaSchema = z.object({
  id: z.string().describe("Short unique id, e.g. 'i1'"),
  title: z.string(),
  format: z.enum(FORMATS),
  platforms: z.array(Platform),
  goal: z.enum(GOALS),
  pillar: z.string().describe("One of the brand's content pillars"),
  trend: z.string().describe("Name of the trend it rides, or 'Evergreen'"),
  day: z.string().nullable().describe("ISO date (YYYY-MM-DD) to post it, for forecast briefs; null otherwise"),
  hook: z.string().describe("The first line or first two seconds, word for word"),
  concept: z.string().describe("The idea in two to four sentences"),
  why_it_works: z.string().describe("Why this will earn reach and/or enquiries, tied to the trend evidence"),
  scores: z.object({
    reach: z.number().describe("0-100 predicted reach / virality potential"),
    business: z.number().describe("0-100 predicted enquiries / design-studio starts"),
    ease: z.number().describe("0-100 how easy to produce this week with a small team"),
    brand_fit: z.number().describe("0-100 fit with the premium brand"),
  }),
  reel: z
    .object({
      duration_seconds: z.number(),
      audio: z.string().describe("Audio direction; name a trending sound only if verified, otherwise describe the style"),
      shots: z.array(ShotSchema),
      edit_notes: z.string(),
    })
    .nullable()
    .describe("Required for reel, short and story formats; null otherwise"),
  slides: z.array(SlideSchema).nullable().describe("Required for carousel format; null otherwise"),
  static_design: z
    .object({
      headline: z.string(),
      subline: z.string(),
      visual: z.string(),
      layout: z.string(),
      palette: z.array(z.string()).describe("Hex colours"),
    })
    .nullable()
    .describe("Required for static and pin formats; null otherwise"),
  pinterest: z
    .object({
      pin_title: z.string(),
      pin_description: z.string(),
      board: z.string(),
      keywords: z.array(z.string()),
      alt_text: z.string(),
    })
    .nullable()
    .describe("Required when the idea is for Pinterest; null otherwise"),
  moodboard_searches: z.array(z.string()).describe("2-4 Pinterest search phrases for visual reference"),
  caption: z.string(),
  hashtags: z.array(z.string()),
  cta: z.string(),
  lead_capture: z.string().nullable().describe("Lead mechanic, e.g. comment keyword to DM, link to the 3D studio; null for pure brand posts"),
  post_time: z.string().describe("Suggested day and UK time"),
  production: z.string().describe("What to film or design, props, who, and how long it takes"),
});

export const DaySchema = z.object({
  date: z.string().describe("YYYY-MM-DD"),
  label: z.string().describe("e.g. 'Friday 27 November: Black Friday'"),
  moments: z.array(z.string()),
  focus: z.string().describe("The one thing that day's content should achieve"),
  idea_ids: z.array(z.string()),
  prep: z.string().describe("What to film, design or schedule the day before"),
});

export const BriefSchema = z.object({
  headline: z.string().describe("One line that sums up the opportunity today"),
  summary: z.string().describe("Three to five sentences: what is moving and what we should do about it"),
  trends: z.array(TrendSchema),
  ideas: z.array(IdeaSchema),
  days: z.array(DaySchema).nullable().describe("Three-day plan for forecast briefs; null for daily briefs"),
  watch_outs: z.array(z.string()).describe("Things to avoid or check (licensing, claims, tone)"),
  sources: z.array(z.object({ title: z.string(), url: z.string() })),
});

export const SingleIdeaSchema = z.object({ idea: IdeaSchema });

export const BrandUpdateSchema = z.object({
  summary: z.string().describe("What was learned and from where"),
  updates: z.object({
    positioning: z.string().nullable(),
    location: z.string().nullable(),
    service_area: z.string().nullable(),
    services: z.array(z.string()).nullable(),
    differentiators: z.array(z.string()).nullable(),
    proof: z.array(z.string()).nullable().describe("Only verifiable proof found on the site or profiles"),
    social: z
      .object({
        instagram: z.string().nullable(),
        facebook: z.string().nullable(),
        tiktok: z.string().nullable(),
        youtube: z.string().nullable(),
        pinterest: z.string().nullable(),
      })
      .nullable(),
    offers: z.array(z.string()).nullable(),
    ctas: z.array(z.string()).nullable(),
    voice_notes: z.string().nullable(),
  }),
  sources: z.array(z.string()),
});
