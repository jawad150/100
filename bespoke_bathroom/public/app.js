// Bespoke Bathroom UK · Social Studio (front end). Everything updates in place: no page reloads.

// ------------------------------------------------------------------ icons
const I = {
  instagram: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
  tiktok: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M16.6 5.8A4.3 4.3 0 0 1 15.5 3h-3.1v12.4a2.6 2.6 0 1 1-2.6-2.6c.3 0 .5 0 .8.1V9.7a5.7 5.7 0 1 0 4.9 5.7V9.1a7.3 7.3 0 0 0 4.3 1.4V7.4a4.3 4.3 0 0 1-3.2-1.6z"/></svg>',
  youtube: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8zM10 15V9l5.2 3z"/></svg>',
  facebook: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 8h3V4h-3a4 4 0 0 0-4 4v2H7v4h3v8h4v-8h3l1-4h-4V8.5c0-.3.2-.5.5-.5z"/></svg>',
  pinterest: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-3.6 19.3c-.1-.8-.2-2 0-2.9l1.2-5s-.3-.6-.3-1.5c0-1.4.8-2.5 1.8-2.5.9 0 1.3.6 1.3 1.4 0 .9-.5 2.1-.8 3.3-.2 1 .5 1.8 1.5 1.8 1.8 0 3.1-1.9 3.1-4.6 0-2.4-1.7-4.1-4.2-4.1a4.4 4.4 0 0 0-4.6 4.4c0 .9.3 1.8.8 2.3.1.1.1.2.1.3l-.3 1.2c0 .2-.2.3-.4.2-1.3-.6-2.1-2.5-2.1-4 0-3.3 2.4-6.3 6.9-6.3 3.6 0 6.4 2.6 6.4 6 0 3.6-2.3 6.5-5.4 6.5-1.1 0-2.1-.6-2.4-1.2l-.7 2.5c-.2.9-.9 2.1-1.3 2.8A10 10 0 1 0 12 2z"/></svg>',
  search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
  spark: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M12 3l1.9 5.6L19.5 10l-5.6 1.9L12 17.5l-1.9-5.6L4.5 10l5.6-1.4z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/></svg>',
  calendar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3.5" y="5" width="17" height="15.5" rx="3"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>',
  download: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v11m0 0 4.5-4.5M12 15l-4.5-4.5M5 19.5h14"/></svg>',
  gear: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>',
  sun: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
  moon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/></svg>',
  x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>',
  copy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="8" y="8" width="12" height="12" rx="3"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></svg>',
  plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
  refresh: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M20 11a8 8 0 0 0-14.6-4.5L4 8m0-4v4h4M4 13a8 8 0 0 0 14.6 4.5L20 16m0 4v-4h-4"/></svg>',
  trash: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V4h6v3"/></svg>',
  key: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 6l3 3M15 8l2 2"/></svg>',
  brain: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 3 3V4zM15 4a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-3 3V4z"/></svg>',
  stop: '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2.5"/></svg>',
  open: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4h6v6M20 4l-9 9M18 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4"/></svg>',
};

const PLATFORMS = [
  ["instagram", "Instagram"],
  ["tiktok", "TikTok"],
  ["youtube", "YouTube"],
  ["facebook", "Facebook"],
];
const P_LABEL = { instagram: "Instagram", tiktok: "TikTok", youtube: "YouTube", facebook: "Facebook", pinterest: "Pinterest" };
const FOCUS = [
  ["balanced", "Balanced", "Reach and enquiries"],
  ["leadgen", "Lead Gen", "Enquiries and designs"],
  ["brand", "Brand & Viral", "Reach, shares, saves"],
];
const FOCUS_LABEL = Object.fromEntries(FOCUS.map(([k, l]) => [k, l]));
const FORMAT_LABEL = { reel: "Reel", carousel: "Carousel", static: "Static", pin: "Pin", story: "Story", short: "Short" };
const GOAL_LABEL = { lead_gen: "Lead gen", brand: "Brand", viral: "Viral", community: "Community" };
const STATUSES = [
  ["planned", "Planned"],
  ["scripted", "Scripted"],
  ["shot", "Shot / designed"],
  ["scheduled", "Scheduled"],
  ["posted", "Posted"],
];

// ------------------------------------------------------------------ state
const S = {
  view: "studio",
  status: null,
  briefs: [],
  current: null,
  focus: "balanced",
  sources: new Set(["instagram", "tiktok", "youtube", "facebook"]),
  pinterest: false,
  job: null,
  live: null,
  filter: { format: "all", goal: "all" },
  plan: null,
  brand: null,
  strategy: null,
  autoTried: false,
};

// ------------------------------------------------------------------ helpers
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const esc = (v) =>
  String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const nl = (v) => esc(v).replace(/\n/g, "<br>");

async function api(path, opts = {}) {
  const res = await fetch(path, {
    ...opts,
    headers: opts.body ? { "Content-Type": "application/json" } : undefined,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(data.error || `Request failed (${res.status})`);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

function toast(msg, type = "") {
  const el = document.createElement("div");
  el.className = `toast glass ${type}`;
  el.textContent = msg;
  $("#toasts").append(el);
  setTimeout(() => {
    el.classList.add("out");
    setTimeout(() => el.remove(), 400);
  }, type === "err" ? 6000 : 3200);
}

async function copy(text, label = "Copied") {
  try {
    await navigator.clipboard.writeText(text);
    toast(label);
  } catch {
    const t = document.createElement("textarea");
    t.value = text;
    document.body.append(t);
    t.select();
    document.execCommand("copy");
    t.remove();
    toast(label);
  }
}

const niceDate = (iso, opts = { weekday: "long", day: "numeric", month: "long" }) =>
  new Date(`${iso}T12:00:00Z`).toLocaleDateString("en-GB", { ...opts, timeZone: "UTC" });
const timeOf = (iso) => new Date(iso).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", timeZone: "Europe/London" });
const money = (n) => (n == null ? "" : `$${Number(n).toFixed(2)}`);

function greeting() {
  const h = Number(new Date().toLocaleString("en-GB", { hour: "2-digit", hour12: false, timeZone: "Europe/London" }));
  return h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening";
}

function ring(v, small = false) {
  return `<div class="ring ${small ? "small" : ""}" style="--v:${Number(v) || 0}"><b>${Number(v) || 0}</b></div>`;
}

function hostOf(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

const pinSearch = (q) => `https://www.pinterest.co.uk/search/pins/?q=${encodeURIComponent(q)}`;

// ------------------------------------------------------------------ navigation
function setView(view, push = true) {
  if (!["studio", "planner", "history", "brand", "strategy"].includes(view)) view = "studio";
  S.view = view;
  const swap = () => {
    $$(".view").forEach((v) => (v.hidden = v.dataset.view !== view));
    $$(".tab").forEach((t) => t.classList.toggle("active", t.dataset.view === view));
    moveGlider();
    render(view);
  };
  if (document.startViewTransition && push) document.startViewTransition(swap);
  else swap();
  if (push && location.hash !== `#${view}`) history.replaceState(null, "", `#${view}`);
}

function moveGlider() {
  const active = $(".tab.active");
  const glider = $(".tab-glider");
  if (!active || !glider) return;
  glider.style.width = `${active.offsetWidth}px`;
  glider.style.transform = `translateX(${active.offsetLeft}px)`;
}

function render(view = S.view) {
  ({ studio: renderStudio, planner: renderPlanner, history: renderHistory, brand: renderBrand, strategy: renderStrategy })[view]?.();
}

// ------------------------------------------------------------------ status
function updateStatusPill() {
  const pill = $("#statusPill");
  const label = pill.querySelector("span");
  pill.className = "status-pill";
  if (S.job) {
    pill.classList.add("busy");
    label.textContent = S.job.type === "learn" ? "Learning the brand" : "Researching";
  } else if (!S.status?.hasKey) {
    pill.classList.add("off");
    label.textContent = "Add API key";
  } else {
    label.textContent = S.status?.todayDaily ? "Up to date" : "Ready";
  }
}

async function loadStatus() {
  S.status = await api("/api/status");
  S.briefs = await api("/api/briefs");
  updateStatusPill();
  return S.status;
}

// ------------------------------------------------------------------ studio
function renderStudio() {
  const root = $("#view-studio");
  const st = S.status;
  if (!st) {
    root.innerHTML = `<div class="skeleton" style="height:340px"></div>`;
    return;
  }
  const brief = S.current;
  const b = brief?.brief;
  const fresh = st.todayDaily
    ? `<span class="fresh"><span class="dot"></span>Today's brief ready · researched <b>${timeOf(st.todayDaily.created_at)}</b></span>`
    : `<span class="fresh stale"><span class="dot"></span>Not researched yet today</span>`;
  const focusIdx = FOCUS.findIndex(([k]) => k === S.focus);

  root.innerHTML = `
  <section class="hero glass">
    <div class="hero-left">
      <span class="eyebrow">${esc(st.todayNice)}</span>
      <h1>${greeting()}.<br><em>Here's what's moving.</em></h1>
      <p class="lede">Your trend desk for Bespoke Bathroom UK. It researches Instagram, TikTok, YouTube, Facebook and Pinterest, then turns what is trending into reels, carousels and posts that fit the brand and bring in designs.</p>
      ${fresh}
      <div class="hero-stats">
        <div class="stat"><b>${b ? b.ideas.length : "0"}</b><span>Ideas</span></div>
        <div class="stat"><b>${b ? b.trends.length : "0"}</b><span>Trends</span></div>
        <div class="stat"><b>${b ? Math.max(...b.ideas.map((i) => i.scores?.overall ?? 0)) : "0"}</b><span>Top score</span></div>
      </div>
    </div>
    <div class="hero-right">
      <div>
        <div class="ctl-label"><span class="eyebrow">Focus</span><span>What should the research chase?</span></div>
        <div class="segmented" id="focusSeg">
          <span class="glider" style="transform:translateX(${focusIdx * 100}%)"></span>
          ${FOCUS.map(([k, l, d]) => `<button data-focus="${k}" class="${S.focus === k ? "on" : ""}"><b>${l}</b><small>${d}</small></button>`).join("")}
        </div>
      </div>
      <div>
        <div class="ctl-label"><span class="eyebrow">Reels and video trends</span><span>Tap to include</span></div>
        <div class="platforms" id="platforms">
          ${PLATFORMS.map(([k, l]) => `<button class="toggle ${S.sources.has(k) ? "on" : ""}" data-src="${k}"><span class="tick"></span>${I[k]}${l}</button>`).join("")}
        </div>
      </div>
      <div class="pin-lab ${S.pinterest ? "on" : ""}" id="pinLab" role="switch" aria-checked="${S.pinterest}" tabindex="0">
        <span class="pin-icon">${I.pinterest}</span>
        <span><b>Pinterest Lab</b><small>Research Pinterest trends and build static post and carousel ideas from them</small></span>
        <span class="switch"></span>
      </div>
      <div class="actions">
        <button class="btn primary" id="researchBtn" ${S.job ? "disabled" : ""}>${I.search}Research today</button>
        <button class="btn" id="updateBtn" ${S.job ? "disabled" : ""}>${I.calendar}Update · next 3 days</button>
        <a class="btn" id="pdfBtn" ${brief ? `href="/api/briefs/${encodeURIComponent(brief.id)}/pdf" download` : 'aria-disabled="true"'}>${I.download}Download PDF</a>
      </div>
    </div>
  </section>
  <div id="liveSlot"></div>
  <div id="noticeSlot"></div>
  <div id="briefSlot"></div>`;

  bindStudioControls();
  renderLive();
  renderNotice();
  renderBriefArea();
}

function bindStudioControls() {
  $$("#focusSeg button").forEach((btn) =>
    btn.addEventListener("click", () => {
      S.focus = btn.dataset.focus;
      const idx = FOCUS.findIndex(([k]) => k === S.focus);
      $("#focusSeg .glider").style.transform = `translateX(${idx * 100}%)`;
      $$("#focusSeg button").forEach((b) => b.classList.toggle("on", b === btn));
    })
  );
  $$("#platforms .toggle").forEach((btn) =>
    btn.addEventListener("click", () => {
      const k = btn.dataset.src;
      if (S.sources.has(k)) {
        if (S.sources.size === 1 && !S.pinterest) return toast("Keep at least one platform switched on");
        S.sources.delete(k);
      } else S.sources.add(k);
      btn.classList.toggle("on", S.sources.has(k));
    })
  );
  const pin = $("#pinLab");
  const flipPin = () => {
    S.pinterest = !S.pinterest;
    pin.classList.toggle("on", S.pinterest);
    pin.setAttribute("aria-checked", S.pinterest);
    toast(S.pinterest ? "Pinterest Lab on: the next research builds static and carousel ideas from Pinterest trends" : "Pinterest Lab off");
  };
  pin.addEventListener("click", flipPin);
  pin.addEventListener("keydown", (e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), flipPin()));
  $("#researchBtn").addEventListener("click", () => startResearch("daily"));
  $("#updateBtn").addEventListener("click", () => startResearch("forecast"));
  $("#pdfBtn").addEventListener("click", (e) => {
    if (!S.current) {
      e.preventDefault();
      toast("Run research first, then download the PDF");
    } else toast("Preparing your PDF");
  });
}

function renderNotice() {
  const slot = $("#noticeSlot");
  if (!slot) return;
  if (S.status?.hasKey || S.job) {
    slot.innerHTML = "";
    return;
  }
  slot.innerHTML = `
  <div class="notice glass">
    <span class="n-icon">${I.key}</span>
    <div><b>Switch on live research</b><p>Add your Anthropic API key once. After that, every morning the studio researches the day's trends on its own when you open it. You're looking at the launch brief researched on 26 November.</p></div>
    <button class="btn primary small" id="addKeyBtn">${I.key}Add API key</button>
  </div>`;
  $("#addKeyBtn").addEventListener("click", openSettings);
}

// ------------------------------------------------------------------ research jobs
async function startResearch(kind, { auto = false } = {}) {
  if (S.job) return toast("Research is already running");
  if (!S.status?.hasKey) {
    openSettings();
    return toast("Add your Anthropic API key to run live research", "err");
  }
  const sources = [...S.sources];
  try {
    const { job } = await api("/api/research", {
      method: "POST",
      body: { kind, focus: S.focus, sources, pinterest: S.pinterest },
    });
    toast(auto ? "Good morning. Researching today's trends for you" : kind === "forecast" ? "Planning the next three days" : "Researching today's trends");
    attachJob(job);
  } catch (err) {
    if (err.status === 409 && err.data?.job) attachJob(err.data.job);
    else toast(err.message, "err");
  }
}

function attachJob(job) {
  S.job = job;
  S.live = { stage: "research", text: "Starting research", searches: 0, reads: 0, ideas: 0, cost: 0, feed: [], t0: Date.now() };
  updateStatusPill();
  if (S.view === "studio") {
    $("#researchBtn") && ($("#researchBtn").disabled = true);
    $("#updateBtn") && ($("#updateBtn").disabled = true);
    renderLive();
    renderNotice();
  }
  const es = new EventSource(`/api/jobs/${job.id}/events`);
  S.jobSource = es;
  es.onmessage = (msg) => {
    const e = JSON.parse(msg.data);
    const L = S.live;
    if (!L) return;
    if (e.kind === "stage") {
      L.stage = e.stage;
      L.text = e.text;
    } else if (e.kind === "search") {
      L.searches++;
      L.feed.unshift({ k: "Search", v: `<q>${esc(e.query)}</q>` });
    } else if (e.kind === "fetch") {
      L.reads++;
      L.feed.unshift({ k: "Read", v: esc(e.host) });
    } else if (e.kind === "results") {
      L.feed.unshift({ k: "Found", v: `${e.count} results · ${esc(e.hosts.join(", "))}` });
    } else if (e.kind === "progress") {
      L.ideas = e.count;
    } else if (e.kind === "usage") {
      L.cost = e.usage.cost;
    } else if (e.kind === "done") {
      es.close();
      onJobDone(job, e.result);
      return;
    } else if (e.kind === "error") {
      es.close();
      onJobError(job, e);
      return;
    }
    L.feed = L.feed.slice(0, 40);
    if (job.type === "research") renderLive(true);
    else renderLearnProgress();
  };
  es.onerror = () => {
    if (S.job?.id !== job.id) es.close();
  };
}

async function onJobDone(job, result) {
  S.job = null;
  const live = S.live;
  S.live = null;
  if (job.type === "learn") {
    renderLearnProposal(result);
    updateStatusPill();
    return;
  }
  await loadStatus();
  S.current = await api(`/api/briefs/${encodeURIComponent(result.briefId)}`);
  toast(`Brief ready: ${S.current.brief.ideas.length} ideas in ${Math.round((Date.now() - live.t0) / 60000) || 1} min`);
  if (S.view === "studio") renderStudio();
}

function onJobError(job, e) {
  S.job = null;
  S.live = null;
  updateStatusPill();
  toast(e.message || "Research failed", "err");
  if (e.code === "auth") openSettings();
  if (job.type === "learn") {
    closeModal();
    return;
  }
  if (S.view === "studio") renderStudio();
}

function renderLive(partial = false) {
  const slot = $("#liveSlot");
  if (!slot) return;
  const L = S.live;
  if (!L || !S.job || S.job.type !== "research") {
    slot.innerHTML = "";
    return;
  }
  const stages = [
    ["research", "Scanning platforms"],
    ["dossier", "Writing the dossier"],
    ["ideas", "Building ideas"],
  ];
  const order = stages.map(([k]) => k);
  const cur = order.indexOf(L.stage);
  const meta = S.job.meta ?? {};
  const html = `
  <section class="live glass">
    <div class="live-orb-col">
      <div class="liquid-orb"></div>
      <div class="live-counters">
        <div><b data-c="searches">${L.searches}</b><span>Searches</span></div>
        <div><b data-c="reads">${L.reads}</b><span>Pages read</span></div>
        <div><b data-c="ideas">${L.ideas}</b><span>Ideas</span></div>
        <div><b data-c="cost">${money(L.cost)}</b><span>Cost so far</span></div>
      </div>
    </div>
    <div>
      <span class="eyebrow">${meta.kind === "forecast" ? "Planning the next three days" : "Researching today"} · ${esc(FOCUS_LABEL[meta.focus] ?? "")}${meta.pinterest ? " · Pinterest Lab" : ""}</span>
      <h3 id="liveText">${esc(L.text)}</h3>
      <p class="muted" style="margin:0">This takes two to six minutes. Keep working; the brief appears here when it is ready.</p>
      <div class="stages">${stages
        .map(([k, l], i) => `<span class="stage ${i < cur ? "done" : i === cur ? "now" : ""}"><i></i>${l}</span>`)
        .join("")}</div>
      <ul class="feed" id="liveFeed">${L.feed.map((f) => `<li><span class="k">${f.k}</span><span>${f.v}</span></li>`).join("")}</ul>
      <div style="margin-top:14px"><button class="btn small danger" id="cancelBtn">${I.stop}Cancel</button></div>
    </div>
  </section>`;
  if (partial && slot.querySelector(".live")) {
    // update in place so the orb keeps spinning smoothly
    slot.querySelector("#liveText").textContent = L.text;
    for (const k of ["searches", "reads", "ideas"]) slot.querySelector(`[data-c="${k}"]`).textContent = L[k];
    slot.querySelector('[data-c="cost"]').textContent = money(L.cost);
    slot.querySelector(".stages").innerHTML = stages
      .map(([k, l], i) => `<span class="stage ${i < cur ? "done" : i === cur ? "now" : ""}"><i></i>${l}</span>`)
      .join("");
    const feed = slot.querySelector("#liveFeed");
    const first = L.feed[0];
    if (first && feed.firstElementChild?.dataset.sig !== `${L.feed.length}`) {
      const li = document.createElement("li");
      li.dataset.sig = `${L.feed.length}`;
      li.innerHTML = `<span class="k">${first.k}</span><span>${first.v}</span>`;
      feed.prepend(li);
      while (feed.children.length > 40) feed.lastElementChild.remove();
    }
    return;
  }
  slot.innerHTML = html;
  $("#cancelBtn").addEventListener("click", async () => {
    await api(`/api/jobs/${S.job.id}/cancel`, { method: "POST" }).catch(() => {});
  });
}

// ------------------------------------------------------------------ brief rendering
function briefLabel(m) {
  const kind = m.kind === "forecast" ? "3-day plan" : "Daily";
  return `${kind} · ${FOCUS_LABEL[m.focus] ?? m.focus}${m.pinterest ? " · Pinterest" : ""}`;
}

function renderBriefArea() {
  const slot = $("#briefSlot");
  if (!slot) return;
  const rec = S.current;
  if (!rec) {
    slot.innerHTML = S.job
      ? ""
      : `<div class="notice glass"><span class="n-icon">${I.spark}</span><div><b>No brief yet</b><p>Press Research today to scan the platforms and get today's ideas.</p></div></div>`;
    return;
  }
  const b = rec.brief;
  const recent = S.briefs.slice(0, 8);
  const byId = Object.fromEntries(b.ideas.map((i) => [i.id, i]));
  const picks = (b.top_picks ?? []).map((id) => byId[id]).filter(Boolean);
  const isForecast = rec.kind === "forecast";
  const created = new Date(rec.created_at);

  slot.innerHTML = `
  <div class="brief-bar">
    <span class="eyebrow">Showing</span>
    <div class="brief-switch">${recent
      .map(
        (m) =>
          `<button data-brief="${esc(m.id)}" class="${m.id === rec.id ? "on" : ""}">${esc(niceDate(m.date, { day: "numeric", month: "short" }))} · ${esc(briefLabel(m))}${m.sample ? " · launch" : ""}</button>`
      )
      .join("")}</div>
  </div>

  <section class="summary glass">
    <div>
      <span class="eyebrow">${isForecast ? `Next three days · ${esc(rec.window?.label ?? "")}` : `Daily brief · ${esc(niceDate(rec.date))}`}</span>
      <h2>${esc(b.headline)}</h2>
      <p>${esc(b.summary)}</p>
    </div>
    <div class="meta">
      <span class="badge gold">${esc(FOCUS_LABEL[rec.focus] ?? rec.focus)}</span>
      ${rec.pinterest ? `<span class="badge pin">Pinterest Lab</span>` : ""}
      ${rec.sample ? `<span class="badge teal">Launch brief</span>` : ""}
      <span class="badge">${created.toLocaleDateString("en-GB", { day: "numeric", month: "short", timeZone: "Europe/London" })} · ${timeOf(rec.created_at)}</span>
      ${rec.usage?.cost != null ? `<span class="badge">Cost ${money(rec.usage.cost)}</span>` : ""}
    </div>
  </section>

  <div class="section-head"><div><span class="eyebrow">Best for reach and business today</span><h2>Top picks</h2></div></div>
  <div class="picks">${picks
    .map(
      (i, n) => `
    <article class="pick glass" data-idea="${esc(i.id)}" style="--i:${n}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px">
        <span class="rank">${String(n + 1).padStart(2, "0")}</span>${ring(i.scores?.overall)}
      </div>
      <h3>${esc(i.title)}</h3>
      <p class="hook">“${esc(i.hook)}”</p>
      <div class="foot">
        <div class="tags" style="display:flex;gap:6px;flex-wrap:wrap"><span class="badge gold">${esc(FORMAT_LABEL[i.format] ?? i.format)}</span><span class="badge">${esc(GOAL_LABEL[i.goal] ?? i.goal)}</span>${i.pinterest && i.format !== "pin" ? '<span class="badge pin">+ Pinterest</span>' : ""}</div>
        <span class="faint" style="font-size:12px">${esc(i.post_time)}</span>
      </div>
    </article>`
    )
    .join("")}</div>

  ${
    isForecast && b.days?.length
      ? `<div class="section-head"><div><span class="eyebrow">Film ahead, post on time</span><h2>The next three days</h2></div></div>
  <div class="days">${b.days
    .map(
      (d, n) => `
    <article class="day glass" style="--i:${n}">
      <span class="eyebrow">${esc(niceDate(d.date, { weekday: "long" }))}</span>
      <h3>${esc(d.label)}</h3>
      <div style="display:flex;gap:6px;flex-wrap:wrap">${(d.moments ?? []).map((m) => `<span class="badge">${esc(m)}</span>`).join("")}</div>
      <p class="focus">${esc(d.focus)}</p>
      ${(d.idea_ids ?? [])
        .map((id) => byId[id])
        .filter(Boolean)
        .map((i) => `<div class="mini" data-idea="${esc(i.id)}">${ring(i.scores?.overall, true)}<div><b>${esc(i.title)}</b><small>${esc(FORMAT_LABEL[i.format] ?? i.format)} · ${esc(i.post_time)}</small></div></div>`)
        .join("")}
      <div class="prep"><b>Prep:</b> ${esc(d.prep)}</div>
    </article>`
    )
    .join("")}</div>`
      : ""
  }

  <div class="section-head"><div><span class="eyebrow">${b.trends.length} trends with evidence</span><h2>Trend radar</h2></div><p class="faint">Scroll sideways</p></div>
  <div class="trends">${b.trends
    .map(
      (t, n) => `
    <article class="trend glass" style="--i:${n}">
      <div style="display:flex;justify-content:space-between;gap:10px;align-items:flex-start"><h4>${esc(t.name)}</h4>${ring(t.brand_fit, true)}</div>
      <div class="row">${(t.platforms ?? []).map((p) => `<span class="badge">${esc(P_LABEL[p] ?? p)}</span>`).join("")}<span class="badge momentum-${esc(t.momentum)}">${esc(t.momentum)}</span><span class="badge">${esc(t.lifespan)}</span></div>
      <p>${esc(t.what_it_is)}</p>
      <p class="faint" style="font-size:12.5px">${esc(t.why_now)}</p>
      <div class="use">${esc(t.how_we_use_it)}</div>
      <div class="row">${(t.sources ?? []).slice(0, 3).map((u) => `<a class="src" href="${esc(u)}" target="_blank" rel="noopener">${esc(hostOf(u))} ↗</a>`).join(" · ")}</div>
    </article>`
    )
    .join("")}</div>

  <div class="section-head">
    <div><span class="eyebrow">Tap any idea for the full script, caption and moodboards</span><h2>All ideas</h2></div>
    <div class="filters" id="ideaFilters">
      ${[["all", "All"], ["reel", "Reels"], ["carousel", "Carousels"], ["static", "Statics"], ["pin", "Pins"], ["story", "Stories"]]
        .filter(([k]) => k === "all" || b.ideas.some((i) => i.format === k || (k === "reel" && i.format === "short")))
        .map(([k, l]) => `<button data-format="${k}" class="${S.filter.format === k ? "on" : ""}">${l}</button>`)
        .join("")}
      <span style="width:8px"></span>
      ${[["all", "Any goal"], ["lead_gen", "Lead gen"], ["brand", "Brand"], ["viral", "Viral"]]
        .map(([k, l]) => `<button data-goal="${k}" class="${S.filter.goal === k ? "on" : ""}">${l}</button>`)
        .join("")}
    </div>
  </div>
  <div class="ideas" id="ideasGrid"></div>

  <div class="section-head"><div><span class="eyebrow">Check before posting</span><h2>Watch-outs</h2></div></div>
  <div class="watch glass"><ul>${(b.watch_outs ?? []).map((w) => `<li>${esc(w)}</li>`).join("")}</ul></div>

  <div class="section-head"><div><span class="eyebrow">Evidence</span><h2>Sources</h2></div></div>
  <div class="sources glass">${(b.sources ?? [])
    .map((s) => `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}<small>${esc(hostOf(s.url))}</small></a>`)
    .join("")}</div>`;

  renderIdeasGrid();
  $$("[data-brief]", slot).forEach((btn) =>
    btn.addEventListener("click", async () => {
      S.current = await api(`/api/briefs/${encodeURIComponent(btn.dataset.brief)}`);
      S.filter = { format: "all", goal: "all" };
      renderStudio();
    })
  );
  $$("#ideaFilters button", slot).forEach((btn) =>
    btn.addEventListener("click", () => {
      if (btn.dataset.format) S.filter.format = btn.dataset.format;
      if (btn.dataset.goal) S.filter.goal = btn.dataset.goal;
      $$("#ideaFilters button").forEach((x) =>
        x.classList.toggle("on", (x.dataset.format && x.dataset.format === S.filter.format) || (x.dataset.goal && x.dataset.goal === S.filter.goal))
      );
      renderIdeasGrid();
    })
  );
  slot.addEventListener("click", (e) => {
    const el = e.target.closest("[data-idea]");
    if (el && !e.target.closest("a")) openIdea(el.dataset.idea);
  });
}

function renderIdeasGrid() {
  const grid = $("#ideasGrid");
  if (!grid || !S.current) return;
  const { format, goal } = S.filter;
  const ideas = S.current.brief.ideas.filter(
    (i) => (format === "all" || i.format === format || (format === "reel" && i.format === "short")) && (goal === "all" || i.goal === goal)
  );
  grid.innerHTML = ideas.length
    ? ideas
        .map(
          (i, n) => `
    <article class="idea glass" data-idea="${esc(i.id)}" style="--i:${n}">
      <div class="top"><div class="tags" style="display:flex;gap:6px;flex-wrap:wrap"><span class="badge gold">${esc(FORMAT_LABEL[i.format] ?? i.format)}</span><span class="badge">${esc(GOAL_LABEL[i.goal] ?? i.goal)}</span>${i.day ? `<span class="badge teal">${esc(niceDate(i.day, { weekday: "short", day: "numeric" }))}</span>` : ""}</div>${ring(i.scores?.overall, true)}</div>
      <h3>${esc(i.title)}</h3>
      <p class="hook">${esc(i.hook)}</p>
      <div class="tags" style="display:flex;gap:6px;flex-wrap:wrap">${(i.platforms ?? []).map((p) => `<span class="badge">${esc(P_LABEL[p] ?? p)}</span>`).join("")}</div>
      <div class="bars">${[["reach", "Reach"], ["business", "Leads"], ["ease", "Ease"], ["brand_fit", "Fit"]]
        .map(([k, l]) => `<div class="bar" style="--v:${i.scores?.[k] ?? 0}"><span>${l}<b>${i.scores?.[k] ?? 0}</b></span><i></i></div>`)
        .join("")}</div>
    </article>`
        )
        .join("")
    : `<div class="empty">No ideas match these filters.</div>`;
}

// ------------------------------------------------------------------ idea drawer
function findIdea(id) {
  return S.current?.brief?.ideas?.find((i) => i.id === id);
}

function ideaText(i) {
  const lines = [`${i.title}`, "", `HOOK: ${i.hook}`, "", i.concept, ""];
  if (i.reel?.shots?.length) {
    lines.push(`SCRIPT (${i.reel.duration_seconds}s) · Audio: ${i.reel.audio}`);
    for (const s of i.reel.shots) lines.push(`${s.time} | ${s.visual} | Text: ${s.on_screen_text}${s.voiceover ? ` | VO: ${s.voiceover}` : ""}`);
    lines.push(`Edit: ${i.reel.edit_notes}`, "");
  }
  if (i.slides?.length) {
    lines.push("SLIDES");
    for (const s of i.slides) lines.push(`${s.slide}. ${s.headline}: ${s.body} [${s.visual}]`);
    lines.push("");
  }
  if (i.static_design) lines.push(`DESIGN: ${i.static_design.headline} / ${i.static_design.subline}`, i.static_design.visual, "");
  if (i.pinterest) lines.push(`PIN: ${i.pinterest.pin_title}`, i.pinterest.pin_description, "");
  lines.push("CAPTION", i.caption, "", (i.hashtags ?? []).join(" "), "", `CTA: ${i.cta}`);
  if (i.lead_capture) lines.push(`Lead capture: ${i.lead_capture}`);
  lines.push(`Post: ${i.post_time}`, `Production: ${i.production}`);
  return lines.join("\n");
}

function ideaDetailHTML(i, { planItem } = {}) {
  const tags = `${(i.platforms ?? []).map((p) => `<span class="badge">${esc(P_LABEL[p] ?? p)}</span>`).join("")}<span class="badge">${esc(i.pillar)}</span><span class="badge teal">${esc(i.post_time)}</span>`;
  return `
  <button class="icon-btn close-x" data-close aria-label="Close">${I.x}</button>
  <div class="d-head">
    <div>
      <span class="eyebrow">${esc(FORMAT_LABEL[i.format] ?? i.format)} · ${esc(GOAL_LABEL[i.goal] ?? i.goal)} · Trend: ${esc(i.trend)}</span>
      <h2 id="drawerTitle">${esc(i.title)}</h2>
      <div style="display:flex;gap:6px;flex-wrap:wrap">${tags}</div>
    </div>
  </div>
  <div class="d-actions">
    ${planItem ? "" : `<button class="btn small primary" data-act="plan">${I.plus}Add to planner</button>`}
    <button class="btn small" data-act="copy-caption">${I.copy}Copy caption</button>
    <button class="btn small" data-act="copy-all">${I.copy}Copy everything</button>
  </div>
  <div class="bars" style="grid-template-columns:repeat(5,1fr);margin-top:8px">${[["overall", "Overall"], ["reach", "Reach"], ["business", "Business"], ["ease", "Ease"], ["brand_fit", "Fit"]]
    .map(([k, l]) => `<div class="bar" style="--v:${i.scores?.[k] ?? 0}"><span>${l}<b>${i.scores?.[k] ?? 0}</b></span><i></i></div>`)
    .join("")}</div>

  ${planItem ? planControlsHTML(planItem) : ""}

  <div class="d-block"><h4>Hook</h4><div class="hook-box">${esc(i.hook)}</div></div>
  <div class="d-block"><h4>The idea</h4><p>${nl(i.concept)}</p></div>
  <div class="d-block"><h4>Why it works</h4><p>${nl(i.why_it_works)}</p></div>
  ${
    i.reel?.shots?.length
      ? `<div class="d-block"><h4>${esc(FORMAT_LABEL[i.format] ?? "Video")} script · ${esc(i.reel.duration_seconds)} seconds</h4>
      <div class="shots">${i.reel.shots
        .map((s) => `<div class="shot"><div class="t">${esc(s.time)}</div><div><div class="v">${esc(s.visual)}</div>${s.on_screen_text ? `<div class="ost">${esc(s.on_screen_text)}</div>` : ""}${s.voiceover ? `<div class="vo">VO: ${esc(s.voiceover)}</div>` : ""}</div></div>`)
        .join("")}</div>
      <dl class="kv" style="margin-top:12px"><dt>Audio</dt><dd>${esc(i.reel.audio)}</dd><dt>Edit notes</dt><dd>${esc(i.reel.edit_notes)}</dd></dl></div>`
      : ""
  }
  ${
    i.slides?.length
      ? `<div class="d-block"><h4>Carousel · ${i.slides.length} slides</h4><div class="slides">${i.slides
          .map((s) => `<div class="slide"><span class="n">${esc(s.slide)} / ${i.slides.length}</span><h5>${esc(s.headline)}</h5><p>${esc(s.body)}</p><span class="vis">${esc(s.visual)}</span></div>`)
          .join("")}</div></div>`
      : ""
  }
  ${
    i.static_design
      ? `<div class="d-block"><h4>Design</h4><div class="mock" style="${i.static_design.palette?.[0] ? `background:${esc(i.static_design.palette[0])}` : ""}"><h5>${esc(i.static_design.headline)}</h5><p>${esc(i.static_design.subline)}</p></div>
      <dl class="kv" style="margin-top:12px"><dt>Visual</dt><dd>${esc(i.static_design.visual)}</dd><dt>Layout</dt><dd>${esc(i.static_design.layout)}</dd></dl>
      <div class="palette">${(i.static_design.palette ?? []).map((c) => `<span><i style="background:${esc(c)}"></i>${esc(c)}</span>`).join("")}</div></div>`
      : ""
  }
  ${
    i.pinterest
      ? `<div class="d-block"><h4>Pinterest <button class="btn small ghost" data-act="copy-pin">${I.copy}Copy pin</button></h4>
      <dl class="kv"><dt>Pin title</dt><dd><b>${esc(i.pinterest.pin_title)}</b></dd><dt>Description</dt><dd>${esc(i.pinterest.pin_description)}</dd><dt>Board</dt><dd>${esc(i.pinterest.board)}</dd><dt>Alt text</dt><dd>${esc(i.pinterest.alt_text)}</dd></dl>
      <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:10px">${(i.pinterest.keywords ?? []).map((k) => `<span class="badge pin">${esc(k)}</span>`).join("")}</div></div>`
      : ""
  }
  <div class="d-block"><h4>Caption <button class="btn small ghost" data-act="copy-caption">${I.copy}Copy</button></h4><div class="copy-box">${esc(i.caption)}\n\n${esc((i.hashtags ?? []).join(" "))}</div></div>
  <div class="d-block"><h4>Call to action</h4><p><b style="color:var(--text)">${esc(i.cta)}</b></p>${i.lead_capture ? `<p style="margin-top:6px">Lead capture: ${esc(i.lead_capture)}</p>` : ""}</div>
  <div class="d-block"><h4>Production</h4><p>${nl(i.production)}</p></div>
  ${
    i.moodboard_searches?.length
      ? `<div class="d-block"><h4>Pinterest moodboards</h4><div class="links">${i.moodboard_searches
          .map((q) => `<a class="btn small" href="${pinSearch(q)}" target="_blank" rel="noopener">${I.pinterest}${esc(q)}</a>`)
          .join("")}</div></div>`
      : ""
  }
  ${
    planItem
      ? ""
      : `<div class="d-block"><h4>Rework with the agent</h4>
      <div class="rework">
        ${["More lead gen", "Shorter and punchier", "More premium", "Make it a carousel", "Use a trending meme format"].map((t) => `<button class="btn small" data-rework="${esc(t)}">${esc(t)}</button>`).join("")}
      </div>
      <div class="rework" style="margin-top:8px"><input type="text" id="reworkInput" placeholder="Or say what to change, e.g. film it in the showroom" /><button class="btn small primary" data-rework-custom>${I.refresh}Rework</button></div></div>`
  }`;
}

function openDrawer(html) {
  $("#drawerBody").innerHTML = html;
  $("#drawer").classList.add("open");
  $("#drawer").setAttribute("aria-hidden", "false");
  $("#drawerBody").scrollTop = 0;
}
function closeDrawer() {
  $("#drawer").classList.remove("open");
  $("#drawer").setAttribute("aria-hidden", "true");
}

function openIdea(id) {
  const idea = findIdea(id);
  if (!idea) return;
  openDrawer(ideaDetailHTML(idea));
  bindIdeaActions(idea);
}

function bindIdeaActions(idea, planItem) {
  const body = $("#drawerBody");
  body.querySelectorAll("[data-act]").forEach((btn) =>
    btn.addEventListener("click", async () => {
      const act = btn.dataset.act;
      if (act === "copy-caption") copy(`${idea.caption}\n\n${(idea.hashtags ?? []).join(" ")}`, "Caption copied");
      if (act === "copy-all") copy(ideaText(idea), "Full post copied");
      if (act === "copy-pin" && idea.pinterest) copy(`${idea.pinterest.pin_title}\n\n${idea.pinterest.pin_description}`, "Pin copy copied");
      if (act === "plan") {
        await api("/api/plan", { method: "POST", body: { idea, briefId: S.current?.id, date: idea.day ?? S.current?.date ?? null } });
        S.plan = null;
        btn.outerHTML = `<span class="badge gold">In the planner</span>`;
        toast("Added to the planner");
      }
    })
  );
  const doRework = async (instruction, btn) => {
    if (!S.status?.hasKey) return (openSettings(), toast("Add your API key to rework ideas", "err"));
    btn.disabled = true;
    const old = btn.innerHTML;
    btn.innerHTML = `${I.refresh}Reworking…`;
    try {
      const { idea: next, top_picks } = await api("/api/rework", { method: "POST", body: { briefId: S.current.id, ideaId: idea.id, instruction } });
      const list = S.current.brief.ideas;
      list[list.findIndex((x) => x.id === idea.id)] = next;
      S.current.brief.top_picks = top_picks;
      openIdea(next.id);
      renderBriefArea();
      toast("Idea reworked");
    } catch (err) {
      toast(err.message, "err");
      btn.disabled = false;
      btn.innerHTML = old;
    }
  };
  body.querySelectorAll("[data-rework]").forEach((btn) => btn.addEventListener("click", () => doRework(btn.dataset.rework, btn)));
  const custom = body.querySelector("[data-rework-custom]");
  custom?.addEventListener("click", () => {
    const v = $("#reworkInput").value.trim();
    if (!v) return toast("Say what to change first");
    doRework(v, custom);
  });
  if (planItem) bindPlanControls(planItem);
}

// ------------------------------------------------------------------ planner
function planControlsHTML(item) {
  return `<div class="d-block glass" style="padding:16px;border-radius:18px">
    <div class="form-grid">
      <div class="field"><label>Status</label><select id="pStatus">${STATUSES.map(([k, l]) => `<option value="${k}" ${item.status === k ? "selected" : ""}>${l}</option>`).join("")}</select></div>
      <div class="field"><label>Post date</label><input type="date" id="pDate" value="${esc(item.date ?? "")}" /></div>
      <div class="field wide"><label>Notes</label><textarea id="pNotes" placeholder="Who films it, where, links to assets">${esc(item.notes ?? "")}</textarea></div>
    </div>
    <div style="display:flex;gap:8px;margin-top:12px"><button class="btn small primary" id="pSave">Save</button><button class="btn small danger" id="pRemove">${I.trash}Remove</button></div>
  </div>`;
}

function bindPlanControls(item) {
  $("#pSave").addEventListener("click", async () => {
    const patch = { status: $("#pStatus").value, date: $("#pDate").value || null, notes: $("#pNotes").value };
    Object.assign(item, await api(`/api/plan/${item.id}`, { method: "PATCH", body: patch }));
    toast("Saved");
    renderPlanner();
  });
  $("#pRemove").addEventListener("click", async () => {
    await api(`/api/plan/${item.id}`, { method: "DELETE" });
    S.plan.items = S.plan.items.filter((x) => x.id !== item.id);
    closeDrawer();
    renderPlanner();
    toast("Removed from the planner");
  });
}

async function renderPlanner() {
  const root = $("#view-planner");
  if (!S.plan) {
    root.innerHTML = `<div class="skeleton" style="height:360px;margin-top:20px"></div>`;
    [S.plan, S.strategy] = await Promise.all([api("/api/plan"), S.strategy ?? api("/api/strategy")]);
  }
  const items = S.plan.items;
  // pillar mix vs strategy targets
  const pillarRows = S.strategy?.sections?.find((s) => s.id === "pillars")?.blocks?.find((b) => b.type === "table")?.rows ?? [];
  const norm = (s) => String(s).toLowerCase().replace(/[^a-z]/g, "");
  const total = items.length || 1;
  const mix = pillarRows.map((r) => {
    const n = items.filter((i) => norm(i.idea?.pillar).includes(norm(r[0]).slice(0, 10)) || norm(r[0]).includes(norm(i.idea?.pillar).slice(0, 10))).length;
    return { name: r[0], target: parseInt(r[1], 10) || 0, v: Math.round((n / total) * 100), n };
  });
  const goals = ["lead_gen", "brand", "viral", "community"].map((g) => ({ g, n: items.filter((i) => i.idea?.goal === g).length }));

  root.innerHTML = `
  <div class="section-head"><div><span class="eyebrow">${items.length} ${items.length === 1 ? "piece" : "pieces"} in the pipeline</span><h2>Content planner</h2><p>Drag cards between columns. Tap a card to edit its date, status and notes.</p></div></div>
  <div class="mix glass">
    ${mix.map((m) => `<div class="mix-row" style="--v:${m.v};--t:${m.target}"><span>${esc(m.name)}</span><span class="faint">${m.v}% · target ${m.target}%</span><i></i></div>`).join("")}
    <div class="mix-row wide"><span>Goal mix</span><span class="faint">${goals.map((g) => `${GOAL_LABEL[g.g]} ${g.n}`).join(" · ")}</span></div>
  </div>
  <div class="board" style="margin-top:16px">${STATUSES.map(
    ([k, l]) => `
    <div class="col glass" data-col="${k}">
      <h3><span>${l}</span><span>${items.filter((i) => i.status === k).length}</span></h3>
      ${
        items
          .filter((i) => i.status === k)
          .sort((a, b) => String(a.date ?? "9").localeCompare(String(b.date ?? "9")))
          .map(
            (i) => `<div class="card" draggable="true" data-plan="${i.id}">
          <div class="row"><span class="badge gold">${esc(FORMAT_LABEL[i.idea?.format] ?? "")}</span>${i.date ? `<span>${esc(niceDate(i.date, { weekday: "short", day: "numeric", month: "short" }))}</span>` : `<span>No date</span>`}</div>
          <b>${esc(i.idea?.title)}</b>
          <div class="row">${(i.idea?.platforms ?? []).map((p) => esc(P_LABEL[p] ?? p)).join(" · ")}</div>
        </div>`
          )
          .join("") || `<div class="empty">${k === "planned" ? "Add ideas from the Studio" : "Drop cards here"}</div>`
      }
    </div>`
  ).join("")}</div>`;

  $$(".card[data-plan]", root).forEach((card) => {
    card.addEventListener("dragstart", (e) => {
      card.classList.add("dragging");
      e.dataTransfer.setData("text/plain", card.dataset.plan);
    });
    card.addEventListener("dragend", () => card.classList.remove("dragging"));
    card.addEventListener("click", () => {
      const item = S.plan.items.find((x) => x.id === card.dataset.plan);
      openDrawer(ideaDetailHTML(item.idea, { planItem: item }));
      bindIdeaActions(item.idea, item);
    });
  });
  $$(".col", root).forEach((col) => {
    col.addEventListener("dragover", (e) => {
      e.preventDefault();
      col.classList.add("drop");
    });
    col.addEventListener("dragleave", () => col.classList.remove("drop"));
    col.addEventListener("drop", async (e) => {
      e.preventDefault();
      col.classList.remove("drop");
      const id = e.dataTransfer.getData("text/plain");
      const item = S.plan.items.find((x) => x.id === id);
      if (!item || item.status === col.dataset.col) return;
      item.status = col.dataset.col;
      renderPlanner();
      await api(`/api/plan/${id}`, { method: "PATCH", body: { status: item.status } }).catch((err) => toast(err.message, "err"));
    });
  });
}

// ------------------------------------------------------------------ history
async function renderHistory() {
  const root = $("#view-history");
  S.briefs = await api("/api/briefs");
  const list = S.briefs;
  root.innerHTML = `
  <div class="section-head"><div><span class="eyebrow">${list.length} briefs saved on this computer</span><h2>History</h2><p>Every research run is kept, so you can go back to any day's ideas.</p></div></div>
  <div class="hist">${
    list
      .map(
        (m, n) => `
    <div class="hist-row glass" style="--i:${n}">
      <div><div class="d">${esc(niceDate(m.date, { weekday: "short", day: "numeric", month: "short" }))}</div><span class="faint" style="font-size:12px">${timeOf(m.created_at)}</span></div>
      <div>
        <div class="h">${esc(m.headline ?? "")}</div>
        <div class="tags"><span class="badge gold">${m.kind === "forecast" ? "3-day plan" : "Daily"}</span><span class="badge">${esc(FOCUS_LABEL[m.focus] ?? m.focus)}</span>${m.pinterest ? '<span class="badge pin">Pinterest</span>' : ""}<span class="badge">${m.ideas} ideas</span>${m.cost != null ? `<span class="badge">${money(m.cost)}</span>` : ""}${m.sample ? '<span class="badge teal">Launch brief</span>' : ""}</div>
      </div>
      <div class="acts">
        <button class="btn small" data-open="${esc(m.id)}">${I.open}Open</button>
        <a class="btn small" href="/api/briefs/${encodeURIComponent(m.id)}/pdf" download>${I.download}PDF</a>
        <button class="btn small danger" data-del="${esc(m.id)}" title="Delete">${I.trash}</button>
      </div>
    </div>`
      )
      .join("") || `<div class="empty">No briefs yet. Run your first research from the Studio.</div>`
  }</div>`;
  $$("[data-open]", root).forEach((b) =>
    b.addEventListener("click", async () => {
      S.current = await api(`/api/briefs/${encodeURIComponent(b.dataset.open)}`);
      S.filter = { format: "all", goal: "all" };
      setView("studio");
      window.scrollTo({ top: 0, behavior: "smooth" });
    })
  );
  $$("[data-del]", root).forEach((b) =>
    b.addEventListener("click", async () => {
      if (!confirm("Delete this brief? This cannot be undone.")) return;
      await api(`/api/briefs/${encodeURIComponent(b.dataset.del)}`, { method: "DELETE" });
      if (S.current?.id === b.dataset.del) S.current = null;
      b.closest(".hist-row").remove();
      toast("Brief deleted");
    })
  );
}

// ------------------------------------------------------------------ brand brain
const lines = (arr) => (Array.isArray(arr) ? arr.join("\n") : arr ?? "");
const unlines = (s) => String(s).split("\n").map((x) => x.trim()).filter(Boolean);

async function renderBrand() {
  const root = $("#view-brand");
  S.brand = await api("/api/brand");
  const b = S.brand;
  const field = (key, label, value, { wide, area, hint } = {}) =>
    `<div class="field ${wide ? "wide" : ""}"><label for="f-${key}">${label}</label>${
      area ? `<textarea id="f-${key}" data-k="${key}">${esc(value)}</textarea>` : `<input type="text" id="f-${key}" data-k="${key}" value="${esc(value)}" />`
    }${hint ? `<small>${hint}</small>` : ""}</div>`;

  root.innerHTML = `
  <div class="section-head">
    <div><span class="eyebrow">The agent reads this before every research run</span><h2>Brand Brain</h2><p>Everything the agent knows about Bespoke Bathroom UK. Fill the [ADD] gaps and every idea gets sharper.</p></div>
    <button class="btn" id="learnBtn">${I.brain}Learn from website and socials</button>
  </div>
  <form class="brand-form glass" id="brandForm">
    <h3>Identity</h3>
    <div class="form-grid">
      ${field("name", "Brand name", b.name)}
      ${field("website", "Website", b.website)}
      ${field("tagline", "Tagline", b.tagline)}
      ${field("one_liner", "One-liner", b.one_liner)}
      ${field("location", "Location", b.location)}
      ${field("service_area", "Service area", b.service_area)}
    </div>
    <h3>Social profiles</h3>
    <div class="form-grid">${["instagram", "facebook", "tiktok", "youtube", "pinterest"].map((k) => field(`social.${k}`, P_LABEL[k], b.social?.[k] ?? "")).join("")}</div>
    <h3>Positioning and offer</h3>
    <div class="form-grid">
      ${field("positioning", "Positioning", b.positioning, { wide: true, area: true })}
      ${field("services", "Services (one per line)", lines(b.services), { wide: true, area: true })}
      ${field("differentiators", "What makes us different (one per line)", lines(b.differentiators), { wide: true, area: true })}
      ${field("proof", "Proof: real reviews, numbers, accreditations (one per line)", lines(b.proof), { wide: true, area: true, hint: "Only real, checkable proof. The agent never invents reviews or stats." })}
      ${field("price_positioning", "Price positioning", b.price_positioning, { wide: true, area: true })}
      ${field("offers", "Offers (one per line)", lines(b.offers), { area: true })}
      ${field("ctas", "Calls to action (one per line)", lines(b.ctas), { area: true })}
      ${field("lead_magnets", "Lead magnets (one per line)", lines(b.lead_magnets), { wide: true, area: true })}
    </div>
    <h3>Audiences</h3>
    <div class="stack" id="audiences">${(b.audiences ?? [])
      .map(
        (a, n) => `<div class="form-grid glass" style="padding:16px;border-radius:18px" data-aud="${n}">
        ${field(`aud.${n}.name`, "Audience", a.name)}
        ${field(`aud.${n}.situation`, "Situation", a.situation)}
        ${field(`aud.${n}.pains`, "Pains", a.pains)}
        ${field(`aud.${n}.wants`, "Wants", a.wants)}
      </div>`
      )
      .join("")}</div>
    <h3>Voice</h3>
    <div class="form-grid">
      ${field("voice.personality", "Personality (one per line)", lines(b.voice?.personality), { area: true })}
      ${field("voice.words_we_use", "Words we use (one per line)", lines(b.voice?.words_we_use), { area: true })}
      ${field("voice.do", "Do (one per line)", lines(b.voice?.do), { area: true })}
      ${field("voice.dont", "Don't (one per line)", lines(b.voice?.dont), { area: true })}
      ${field("visual_style", "Visual style", b.visual_style, { wide: true, area: true })}
    </div>
    <h3>Hashtags, competitors and rules</h3>
    <div class="form-grid">
      ${field("hashtags.core", "Core hashtags (one per line)", lines(b.hashtags?.core), { area: true })}
      ${field("hashtags.uk", "UK and local hashtags (one per line)", lines([...(b.hashtags?.uk ?? []), ...(b.hashtags?.local ?? [])]), { area: true })}
      ${field("competitors", "Competitors and benchmarks (one per line)", lines(b.competitors), { area: true })}
      ${field("content_rules", "Content rules (one per line)", lines(b.content_rules), { area: true })}
    </div>
    <p class="faint" style="margin-top:18px;font-size:12.5px">Last updated ${esc(b.updated_at ?? "")}. Source: ${esc(b.source ?? "")}</p>
  </form>
  <div class="sticky-save"><div class="glass"><button class="btn primary" id="saveBrand">Save Brand Brain</button></div></div>`;

  $("#saveBrand").addEventListener("click", saveBrand);
  $("#learnBtn").addEventListener("click", startLearn);
}

function collectBrand() {
  const b = structuredClone(S.brand);
  const get = (k) => $(`[data-k="${CSS.escape(k)}"]`)?.value ?? "";
  for (const k of ["name", "website", "tagline", "one_liner", "location", "service_area", "positioning", "price_positioning", "visual_style"]) b[k] = get(k).trim();
  for (const k of ["services", "differentiators", "proof", "offers", "ctas", "lead_magnets", "competitors", "content_rules"]) b[k] = unlines(get(k));
  b.social = b.social ?? {};
  for (const k of ["instagram", "facebook", "tiktok", "youtube", "pinterest"]) b.social[k] = get(`social.${k}`).trim();
  b.voice = b.voice ?? {};
  for (const k of ["personality", "words_we_use", "do", "dont"]) b.voice[k] = unlines(get(`voice.${k}`));
  b.hashtags = { core: unlines(get("hashtags.core")), uk: unlines(get("hashtags.uk")), local: [] };
  b.audiences = (b.audiences ?? []).map((a, n) => ({
    name: get(`aud.${n}.name`),
    situation: get(`aud.${n}.situation`),
    pains: get(`aud.${n}.pains`),
    wants: get(`aud.${n}.wants`),
  }));
  return b;
}

async function saveBrand() {
  try {
    S.brand = await api("/api/brand", { method: "PUT", body: collectBrand() });
    toast("Brand Brain saved. The next research uses it");
  } catch (err) {
    toast(err.message, "err");
  }
}

async function startLearn() {
  if (!S.status?.hasKey) return (openSettings(), toast("Add your API key so the agent can read the website", "err"));
  try {
    const { job } = await api("/api/brand/learn", { method: "POST", body: { website: $('[data-k="website"]').value } });
    openModal(`<button class="icon-btn close-x" data-close aria-label="Close">${I.x}</button>
      <span class="eyebrow">Brand Brain</span><h2>Learning the brand</h2>
      <p class="muted">Reading the website and searching for social profiles and reviews.</p>
      <div style="display:grid;place-items:center;margin:18px 0"><div class="liquid-orb" style="width:110px;height:110px"></div></div>
      <ul class="feed" id="learnFeed"></ul>`);
    attachJob(job);
  } catch (err) {
    toast(err.message, "err");
  }
}

function renderLearnProgress() {
  const feed = $("#learnFeed");
  if (!feed || !S.live) return;
  feed.innerHTML = S.live.feed.map((f) => `<li><span class="k">${f.k}</span><span>${f.v}</span></li>`).join("");
}

function renderLearnProposal({ proposal }) {
  const u = proposal.updates ?? {};
  const rows = [];
  const add = (key, label, value) => {
    if (value == null || (Array.isArray(value) && !value.length)) return;
    rows.push({ key, label, value });
  };
  add("positioning", "Positioning", u.positioning);
  add("location", "Location", u.location);
  add("service_area", "Service area", u.service_area);
  add("services", "Services", u.services);
  add("differentiators", "Differentiators", u.differentiators);
  add("proof", "Proof", u.proof);
  add("offers", "Offers", u.offers);
  add("ctas", "Calls to action", u.ctas);
  if (u.social) for (const [k, v] of Object.entries(u.social)) if (v) add(`social.${k}`, P_LABEL[k], v);
  add("voice_notes", "Voice notes", u.voice_notes);
  openModal(`<button class="icon-btn close-x" data-close aria-label="Close">${I.x}</button>
    <span class="eyebrow">Brand Brain</span><h2>What the agent learned</h2>
    <p class="muted">${esc(proposal.summary)}</p>
    <div class="stack">${
      rows.length
        ? rows
            .map(
              (r, n) => `<label class="check-row"><input type="checkbox" data-row="${n}" checked /><span><b>${esc(r.label)}</b>${Array.isArray(r.value) ? r.value.map(esc).join("<br>") : esc(r.value)}</span></label>`
            )
            .join("")
        : `<div class="empty">Nothing new found.</div>`
    }</div>
    <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:18px"><button class="btn" data-close>Cancel</button><button class="btn primary" id="applyLearn" ${rows.length ? "" : "disabled"}>Apply selected</button></div>`);
  $("#applyLearn")?.addEventListener("click", async () => {
    const b = structuredClone(S.brand);
    $$("[data-row]").forEach((cb) => {
      if (!cb.checked) return;
      const r = rows[Number(cb.dataset.row)];
      if (r.key.startsWith("social.")) (b.social ??= {})[r.key.slice(7)] = r.value;
      else if (r.key === "voice_notes") b.voice = { ...(b.voice ?? {}), notes: r.value };
      else b[r.key] = r.value;
    });
    b.source = `${b.website} and profiles, learned ${new Date().toLocaleDateString("en-GB")}`;
    S.brand = await api("/api/brand", { method: "PUT", body: b });
    closeModal();
    renderBrand();
    toast("Brand Brain updated");
  });
}

// ------------------------------------------------------------------ strategy
async function renderStrategy() {
  const root = $("#view-strategy");
  S.strategy = S.strategy ?? (await api("/api/strategy"));
  const s = S.strategy;
  const block = (b) => {
    if (b.type === "p") return `<p>${esc(b.text)}</p>`;
    if (b.type === "list") return `<ul>${b.items.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>`;
    if (b.type === "table")
      return `<div style="overflow-x:auto"><table><thead><tr>${b.head.map((h) => `<th>${esc(h)}</th>`).join("")}</tr></thead><tbody>${b.rows
        .map((r) => `<tr>${r.map((c) => `<td>${esc(c)}</td>`).join("")}</tr>`)
        .join("")}</tbody></table></div>`;
    if (b.type === "cards") return `<div class="cards">${b.items.map((c) => `<div><b>${esc(c.title)}</b><p>${esc(c.text)}</p>${c.meta ? `<small>${esc(c.meta)}</small>` : ""}</div>`).join("")}</div>`;
    return "";
  };
  root.innerHTML = `
  <div class="section-head">
    <div><span class="eyebrow">${esc(s.subtitle ?? "")} · updated ${esc(s.updated ?? "")}</span><h2>Social media strategy</h2><p>The plan the agent works inside. Share the PDF with the team.</p></div>
    <a class="btn primary" href="/api/strategy/pdf" download>${I.download}Download strategy PDF</a>
  </div>
  <article class="doc glass">${(s.sections ?? []).map((sec) => `<h3>${esc(sec.title)}</h3>${sec.blocks.map(block).join("")}`).join("")}</article>`;
}

// ------------------------------------------------------------------ settings
function openModal(html) {
  $("#modalPanel").innerHTML = html;
  $("#modal").classList.add("open");
  $("#modal").setAttribute("aria-hidden", "false");
}
function closeModal() {
  $("#modal").classList.remove("open");
  $("#modal").setAttribute("aria-hidden", "true");
}

async function openSettings() {
  const st = await api("/api/settings");
  openModal(`
    <button class="icon-btn close-x" data-close aria-label="Close">${I.x}</button>
    <span class="eyebrow">Settings</span><h2>Research engine</h2>
    <p class="muted">The studio uses Claude with live web search. Your key stays on this computer in data/config.json.</p>
    <div class="stack">
      <div class="field"><label for="sKey">Anthropic API key</label>
        <input type="password" id="sKey" placeholder="${st.keySource ? `Saved (${esc(st.keyPreview || "from .env")}). Paste a new key to replace it` : "sk-ant-..."}" autocomplete="off" />
        <small>Get one at console.anthropic.com. ${st.keySource === "env" ? "Currently read from the .env file." : ""}</small>
      </div>
      <div class="form-grid">
        <div class="field"><label for="sModel">Model</label><select id="sModel">${st.models.map((m) => `<option value="${m.id}" ${st.model === m.id ? "selected" : ""}>${esc(m.label)}</option>`).join("")}</select></div>
        <div class="field"><label for="sDepth">Research depth</label><select id="sDepth"><option value="standard" ${st.depth === "standard" ? "selected" : ""}>Standard (about 15 searches)</option><option value="deep" ${st.depth === "deep" ? "selected" : ""}>Deep (about 30 searches)</option></select></div>
      </div>
      <label class="check-row" style="cursor:pointer"><input type="checkbox" id="sAuto" ${st.autoResearch ? "checked" : ""} /><span><b>Daily auto-research</b>Research today's trends automatically the first time you open the studio each day.</span></label>
      <p class="faint" style="font-size:12px;margin:0">Each run's cost is shown live while it runs and saved with the brief. Server-side fallback is on, so a declined request retries on a fallback model automatically.</p>
      <div style="display:flex;gap:8px;justify-content:flex-end">${st.keySource === "settings" ? `<button class="btn danger" id="sClear">${I.trash}Remove key</button>` : ""}<button class="btn primary" id="sSave">Save settings</button></div>
    </div>`);
  $("#sSave").addEventListener("click", async () => {
    const body = { model: $("#sModel").value, depth: $("#sDepth").value, autoResearch: $("#sAuto").checked };
    const key = $("#sKey").value.trim();
    if (key) body.apiKey = key;
    await api("/api/settings", { method: "PUT", body });
    await loadStatus();
    closeModal();
    renderNotice();
    toast(key ? "Key saved. Live research is on" : "Settings saved");
  });
  $("#sClear")?.addEventListener("click", async () => {
    await api("/api/settings", { method: "PUT", body: { apiKey: "" } });
    await loadStatus();
    closeModal();
    renderNotice();
    toast("Key removed");
  });
}

// ------------------------------------------------------------------ theme + glass sheen
function setThemeIcon() {
  $("#themeBtn").innerHTML = document.documentElement.dataset.theme === "light" ? I.moon : I.sun;
}
$("#themeBtn").addEventListener("click", () => {
  const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
  const apply = () => {
    document.documentElement.dataset.theme = next;
    setThemeIcon();
  };
  document.startViewTransition ? document.startViewTransition(apply) : apply();
  try {
    localStorage.setItem("bb-theme", next);
  } catch {}
});
$("#settingsBtn").innerHTML = I.gear;
$("#settingsBtn").addEventListener("click", openSettings);

let sheenRaf = 0;
document.addEventListener("pointermove", (e) => {
  if (sheenRaf) return;
  sheenRaf = requestAnimationFrame(() => {
    sheenRaf = 0;
    const el = e.target.closest?.(".glass");
    if (!el) return;
    const r = el.getBoundingClientRect();
    el.style.setProperty("--mx", `${((e.clientX - r.left) / r.width) * 100}%`);
    el.style.setProperty("--my", `${((e.clientY - r.top) / r.height) * 100}%`);
  });
});

// ------------------------------------------------------------------ global events
document.addEventListener("click", (e) => {
  if (e.target.closest("[data-close]")) {
    if (e.target.closest("#drawer")) closeDrawer();
    if (e.target.closest("#modal")) closeModal();
  }
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeDrawer();
    closeModal();
  }
});
$$(".tab").forEach((t) => t.addEventListener("click", () => setView(t.dataset.view)));
window.addEventListener("hashchange", () => setView(location.hash.slice(1), false));
window.addEventListener("resize", moveGlider);

// ------------------------------------------------------------------ boot
(async function boot() {
  setThemeIcon();
  setView(location.hash.slice(1) || "studio", false);
  try {
    await loadStatus();
  } catch {
    toast("Cannot reach the studio server. Is it running?", "err");
    return;
  }
  const st = S.status;
  S.focus = st.defaultFocus ?? "balanced";
  S.sources = new Set((st.defaultSources ?? []).filter((s) => s !== "pinterest"));
  if (!S.sources.size) S.sources = new Set(["instagram", "tiktok", "youtube", "facebook"]);
  const pick = st.todayDaily ?? st.latest;
  if (pick) S.current = await api(`/api/briefs/${encodeURIComponent(pick.id)}`).catch(() => null);
  if (st.job) attachJob(st.job);
  render();
  moveGlider();
  // Keep the bot up to date: research today's trends the first time the studio opens each day.
  if (st.autoResearch && st.hasKey && !st.todayDaily && !st.job && !S.autoTried) {
    S.autoTried = true;
    startResearch("daily", { auto: true });
  }
})();
