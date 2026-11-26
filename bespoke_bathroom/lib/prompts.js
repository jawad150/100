// Prompt builders: the brand-trained system prompt and the per-run task prompts.

const FOCUS_TEXT = {
  balanced:
    "BALANCED. Mix reach and enquiries: roughly half the ideas chase reach and saves, half drive people to start a free 3D design.",
  leadgen:
    "LEAD GEN. Research from a business perspective: which trends and formats make a homeowner take the next step. Every idea needs a concrete lead mechanic (comment keyword to DM, studio link, 'talk to a designer', lead form) and a believable path from view to enquiry. Weight the 'business' score.",
  brand:
    "BRAND & VIRAL. Research for page branding and reach: trending formats, sounds, memes and aesthetics that a premium bathroom brand can ride without looking cheap. Optimise for shares, saves, comments and non-follower reach; keep the brand look consistent. Weight the 'reach' score.",
};

const SOURCE_TEXT = {
  instagram: "Instagram (Reels trends, trending audio, carousel formats)",
  tiktok: "TikTok (trends that reach Reels one to two weeks later)",
  youtube: "YouTube (Shorts trends, renovation and home content)",
  facebook: "Facebook (Reels, home-improvement audiences, local groups)",
  pinterest: "Pinterest (Pinterest Trends, Pinterest Predicts, what bathroom pins are being saved)",
};

export function buildSystemPrompt(brand, strategy) {
  const pillars =
    strategy?.sections
      ?.find((s) => s.id === "pillars")
      ?.blocks?.find((b) => b.type === "table")
      ?.rows?.map((r) => `- ${r[0]} (${r[1]}): ${r[2]}`)
      .join("\n") ?? "";
  const series =
    strategy?.sections
      ?.find((s) => s.id === "series")
      ?.blocks?.[0]?.items?.map((i) => `- ${i.title}: ${i.text}`)
      .join("\n") ?? "";

  return `You are the in-house social media strategist, trend researcher and content creator for ${brand.name}. You know this brand better than anyone and you plan content that earns reach and turns it into enquiries.

# The brand (the Brand Brain, maintained by the team)
${JSON.stringify(brand, null, 2)}

# Strategy you work within
The one job of social: get the right homeowner to start a free 3D design in the studio (${brand.website}). Reach brings people in, saves keep them, the studio converts them.

Content pillars:
${pillars}

Signature series you can reuse or adapt:
${series}

Platform roles: Instagram is home base (Reels, carousels, stories, DMs). TikTok is reach and trend testing. YouTube is search and depth (Shorts plus monthly long-form). Facebook reaches local, older homeowners and runs lead forms. Pinterest is evergreen discovery months before people renovate; pins carry keyword-led titles and link to the studio or a product.

# How you write
- British English. No em-dashes and no spaced en-dashes; use full stops, commas, colons or brackets.
- Benefit first, feature second. Show what the room does for the person ("quiet mornings in a room that finally feels like yours"), not adjectives.
- The first line of a caption and the first two seconds of a video show the outcome or the pain, never the logo.
- Cut filler words: elevate, unlock, seamless, world-class, game-changer, innovative, cutting-edge, nestled, tailored solutions, look no further, "whether you're X or Y", "Discover" as an opener.
- Never invent proof: no made-up reviews, client counts, statistics, awards or guarantees. Use only facts from the Brand Brain or your research. Where proof is needed and missing, write a placeholder such as [ADD: real review].
- Prices must match the brand's own figures (VAT included). Budgets in the studio run from £1,000 to £100,000.
- Captions: hook line, two to five short lines, one clear CTA. Few or no emojis. Hashtags: 5 to 10, mixing the brand's core set with trend and topic tags.
- Calm, confident, exact, warm, quietly premium. Never cheap or shouty.

# How you research
- Today's date and the date window are given in each task. Only treat something as a trend if you find evidence from the last 14 days (or a dated upcoming moment). Prefer primary signals (platform newsrooms, TikTok Creative Center, Instagram @creators, YouTube Culture & Trends, Pinterest Trends and Predicts) and reputable trend round-ups (Later, Hootsuite, Sprout Social, Buffer, Metricool, Social Media Today, Tagger) published recently.
- Name a trending sound only when a source confirms it. Otherwise describe the audio style. Remind the team that business accounts cannot use most commercial music: original audio, voiceover or licensed library sounds are the safe default.
- Adapt every trend to the brand: premium, calm, design-led. Drop trends that would look cheap, mock customers, or need a face or home without consent.
- Keep UK context: UK spelling, UK dates and moments, UK prices, UK homeowners.
- Cite the URLs you relied on.`;
}

export function windowDates(kind, today) {
  // today is YYYY-MM-DD (Europe/London)
  const base = new Date(`${today}T12:00:00Z`);
  const fmt = (d) => d.toISOString().slice(0, 10);
  const nice = (d) =>
    d.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }).replace(",", "");
  if (kind === "forecast") {
    const days = [1, 2, 3].map((n) => new Date(base.getTime() + n * 86400000));
    return { dates: days.map(fmt), label: `${nice(days[0])} to ${nice(days[2])}`, days: days.map((d) => ({ iso: fmt(d), nice: nice(d) })) };
  }
  return { dates: [today], label: nice(base), days: [{ iso: today, nice: nice(base) }] };
}

export function researchTask({ kind, focus, sources, pinterest, today, depth }) {
  const win = windowDates(kind, today);
  const srcList = sources.map((s) => `- ${SOURCE_TEXT[s]}`).join("\n");
  const searches = depth === "deep" ? "25 to 35" : "12 to 18";
  const when =
    kind === "forecast"
      ? `Plan the NEXT THREE DAYS: ${win.label}. Find trends that are rising now and will still be live on those days, dated moments on those days (UK events, retail days, holidays, awareness days, weather, sport, TV), and anything the team should film today to be ready.`
      : `Research TODAY: ${win.label}. Find what is trending right now that ${"this brand"} can use today or tomorrow while it is still live.`;

  const todayNice = windowDates("daily", today).label;
  return `Today is ${todayNice} (UK time).

${when}

Focus: ${FOCUS_TEXT[focus]}

Platforms to research:
${srcList}
${
  pinterest
    ? `
PINTEREST LAB IS ON. Go deep on Pinterest: Pinterest Trends and Pinterest Predicts signals for bathrooms and interiors, the aesthetics, colours, materials and layouts people are saving now, seasonal planning behaviour, and the pin styles that perform (static pins, carousel pins, collages, text-on-image guides). Note concrete search phrases the team can open on Pinterest for moodboards. These will drive static post and carousel ideas.`
    : ""
}

Work method:
1. Run about ${searches} focused web searches (and fetch the most useful pages) across the platforms above, home and interiors news, and bathroom design trends. Use the current month and year in queries.
2. Check UK moments in the date window.
3. Look at what comparable bathroom and interiors brands are posting that is working (formats, hooks), without copying them.
4. Keep only what is real and current. Discard anything you cannot evidence.

Then write a RESEARCH DOSSIER in markdown (no JSON yet) with these sections:
## Trends (for each: name, platforms, kind, what it is, evidence of momentum with dates, how ${"Bespoke Bathroom UK"} could use it, brand fit 0-100, momentum, likely lifespan, source URLs)
## Moments in the window (dated)
${pinterest ? "## Pinterest signals (aesthetics, searches, pin formats, moodboard search phrases)\n" : ""}## What is working for comparable brands
## Lead-gen angles${focus === "leadgen" ? " (go deep: offers, objections, DM mechanics, formats that convert)" : ""}
## Watch-outs (licensing, claims, sensitivities)
## Sources (title and URL for every source used)

Aim for 6 to 10 strong trends. Quality over quantity.`;
}

export function synthesisTask({ kind, focus, pinterest, today, dossier, ideaCount }) {
  const win = windowDates(kind, today);
  const mix = pinterest
    ? "At least half the ideas must be Pinterest-led static posts, pins or carousels built from the Pinterest signals (fill static_design or slides, plus the pinterest block with keyword-led pin copy). The rest can be reels."
    : "Mix formats: about half reels (or Shorts), the rest carousels, statics and stories, matched to what the research says is working.";
  const forecastRules =
    kind === "forecast"
      ? `This is a FORECAST for ${win.label}. Set each idea's "day" to one of: ${win.dates.join(", ")}. Spread ideas across all three days (2 to 4 per day). Fill "days" with one entry per date: label (weekday, date and the main moment), moments, the day's focus, the idea ids for that day, and prep (what to film or design the day before).`
      : `This is the DAILY brief for ${win.label}. Set "day" to null on every idea and "days" to null.`;

  return `Here is today's research dossier:

<dossier>
${dossier}
</dossier>

Turn it into the content brief as JSON matching the schema.

Rules:
- ${ideaCount} ideas, ranked best first. Every idea must ride a trend or moment from the dossier (or be marked 'Evergreen' when it is a signature series that suits the day).
- Focus: ${FOCUS_TEXT[focus]}
- ${mix}
- ${forecastRules}
- Reels: 3 to 8 shots with timecodes, word-for-word on-screen text, voiceover where used, audio direction, edit notes. Hook lands in the first two seconds.
- Carousels: 5 to 10 slides, slide 1 is the hook, last slide is the CTA.
- Statics and pins: headline, subline, visual, layout and a palette from the brand colours (#081C26, #174A5C, #F5F2ED, #C5A16B, #E4C99B, #8A6A3B) plus any trend colours.
- moodboard_searches: 2 to 4 phrases the team can type into Pinterest.
- Scores are honest predictions (0-100). Ease reflects a small team with a phone, the 3D studio and access to fitted projects.
- post_time in UK time with the day name.
- Trends: include the 6 to 10 strongest from the dossier with their source URLs.
- watch_outs: specific to today's ideas.
- Follow every writing rule in the system prompt: British English, no em-dashes, no invented proof.`;
}

export function reworkTask({ idea, instruction, focus }) {
  return `Rework this content idea for ${"Bespoke Bathroom UK"}.

Instruction from the team: ${instruction}

Focus: ${FOCUS_TEXT[focus] ?? FOCUS_TEXT.balanced}

Current idea (JSON):
${JSON.stringify(idea, null, 2)}

Return the full reworked idea as JSON in the "idea" field. Keep the same id and day. Keep what already works; change what the instruction asks for. Follow every writing rule in the system prompt.`;
}

export function brandLearnTask({ website, handles }) {
  return `Research the brand's own website and social profiles to update the Brand Brain.

Website: ${website}
Profiles to check if they exist: ${handles.filter(Boolean).join(", ") || "search for them"}

Fetch the website's home page and any about, contact, services, design, fitting and review pages you can find. Search for the brand's Instagram, Facebook, TikTok, YouTube and Pinterest profiles and Google reviews.

Then write a short markdown report: what the brand offers, where it is based and serves, its proof (reviews, accreditations) with quotes, its social handles, its offers and calls to action, and its tone. Only include what you can see on those pages. List the URLs you used.`;
}

export function brandUpdateTask(report) {
  return `From this research report, produce Brand Brain updates as JSON matching the schema. Use null for any field the report does not support. Never invent proof.

<report>
${report}
</report>`;
}
