/* TREATS — motion layer (GSAP + ScrollTrigger + Lenis) */
(() => {
  const html = document.documentElement;
  html.classList.remove("no-js");

  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const finePointer = matchMedia("(hover: hover) and (pointer: fine)").matches;

  if (reduced) html.classList.add("rm");

  /* ---------------------------------------------------------
     Clone hero product illustrations into cards / gallery tiles
     --------------------------------------------------------- */
  const sources = {};
  $$(".hero__products .product").forEach((svg) => (sources[svg.dataset.name] = svg));
  $$("[data-clone]").forEach((host) => {
    const src = sources[host.dataset.clone];
    if (!src) return;
    const copy = src.cloneNode(true);
    copy.querySelectorAll("defs").forEach((d) => d.remove()); // gradients resolve to the hero originals
    copy.removeAttribute("class");
    copy.setAttribute("aria-hidden", "true");
    copy.removeAttribute("role");
    copy.removeAttribute("aria-label");
    (host.querySelector(".pcard__art, .gtile__art") || host).appendChild(copy);
  });

  /* ---------------------------------------------------------
     Text splitting
     --------------------------------------------------------- */
  const splitWords = (el, cls) => {
    const words = el.textContent.trim().split(/\s+/);
    el.innerHTML = words.map((w) => `<span class="${cls}">${w}</span>`).join(" ");
    return $$("." + cls, el);
  };
  $$(".split-words").forEach((el) => splitWords(el, "w"));
  $$(".split-lines").forEach((el) => {
    const tmp = document.createElement("div");
    tmp.innerHTML = el.innerHTML.split(/<br\s*\/?>/i).join(" ");
    const text = tmp.textContent.trim().split(/\s+/);
    el.innerHTML = text.map((w) => `<span class="wm"><span class="wi">${w}</span></span>`).join(" ");
  });
  $$(".split-chars").forEach((el) => {
    el.innerHTML = [...el.textContent].map((c) => `<span class="c">${c}</span>`).join("");
  });

  /* ---------------------------------------------------------
     Menu (works without GSAP)
     --------------------------------------------------------- */
  const burger = $(".nav__burger");
  const menu = $(".menu");
  const setMenu = (open) => {
    document.body.classList.toggle("menu-open", open);
    burger.setAttribute("aria-expanded", String(open));
    burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    menu.setAttribute("aria-hidden", String(!open));
  };
  burger.addEventListener("click", () => setMenu(!document.body.classList.contains("menu-open")));

  if (!window.gsap || !window.ScrollTrigger) {
    $(".loader")?.remove();
    $$("a[href^='#']").forEach((a) => a.addEventListener("click", () => setMenu(false)));
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  /* ---------------------------------------------------------
     Smooth scroll
     --------------------------------------------------------- */
  let lenis = null;
  if (!reduced && window.Lenis) {
    lenis = new Lenis({ duration: 1.15, smoothWheel: true });
    lenis.on("scroll", ScrollTrigger.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
  }

  $$("a[href^='#']").forEach((a) => {
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href");
      const target = id === "#" || id === "#top" ? 0 : $(id);
      if (target === null) return;
      e.preventDefault();
      setMenu(false);
      if (lenis) lenis.scrollTo(target, { duration: 1.4 });
      else if (target === 0) scrollTo({ top: 0 });
      else target.scrollIntoView();
    });
  });

  /* ---------------------------------------------------------
     Global chrome: progress bar, nav hide/show, current section
     --------------------------------------------------------- */
  gsap.to(".progress span", {
    scaleX: 1, ease: "none",
    scrollTrigger: { start: 0, end: "max", scrub: 0.3 },
  });

  const nav = $(".nav");
  ScrollTrigger.create({
    start: 0, end: "max",
    onUpdate: (self) => {
      const y = self.scroll();
      nav.classList.toggle("is-hidden", self.direction === 1 && y > 200 && !document.body.classList.contains("menu-open"));
    },
  });

  // created after the pinned sections (pins add scroll distance), so positions include the pin spacing
  const navCurrent = () => $$(".nav__links a").forEach((a) => {
    const sec = $(a.getAttribute("href"));
    if (!sec) return;
    ScrollTrigger.create({
      trigger: sec, start: "top 50%", end: "bottom 50%", refreshPriority: -1,
      onToggle: (self) => a.classList.toggle("is-current", self.isActive),
    });
  });

  /* ---------------------------------------------------------
     Cursor + magnetic buttons (desktop only)
     --------------------------------------------------------- */
  if (finePointer && !reduced) {
    const cursor = $(".cursor");
    const label = $(".cursor__label");
    const xTo = gsap.quickTo(cursor, "x", { duration: 0.35, ease: "power3" });
    const yTo = gsap.quickTo(cursor, "y", { duration: 0.35, ease: "power3" });
    addEventListener("pointermove", (e) => { xTo(e.clientX); yTo(e.clientY); cursor.style.opacity = 1; }, { passive: true });
    document.addEventListener("pointerleave", () => (cursor.style.opacity = 0));
    $$("[data-cursor], .pcard, .gtile, .store").forEach((el) => {
      el.addEventListener("pointerenter", () => {
        cursor.classList.add("is-big");
        label.textContent = el.dataset.cursor || (el.classList.contains("store") ? "Visit" : "Yum");
      });
      el.addEventListener("pointerleave", () => cursor.classList.remove("is-big"));
    });

    $$(".magnetic").forEach((el) => {
      const mx = gsap.quickTo(el, "x", { duration: 0.6, ease: "elastic.out(1, .4)" });
      const my = gsap.quickTo(el, "y", { duration: 0.6, ease: "elastic.out(1, .4)" });
      el.addEventListener("pointermove", (e) => {
        const r = el.getBoundingClientRect();
        mx((e.clientX - (r.left + r.width / 2)) * 0.3);
        my((e.clientY - (r.top + r.height / 2)) * 0.3);
      });
      el.addEventListener("pointerleave", () => { mx(0); my(0); });
    });
  }

  /* ---------------------------------------------------------
     Loader → hero intro
     --------------------------------------------------------- */
  const heroIntro = () => {
    const tl = gsap.timeline({ defaults: { ease: "expo.out" } });
    tl.from(".hero__title .line > span", { yPercent: 110, duration: 1.2, stagger: 0.1 })
      .from(".eyebrow", { y: 20, autoAlpha: 0, duration: 0.8 }, 0.1)
      .from(".hero__lede, .hero__ctas", { y: 30, autoAlpha: 0, duration: 1, stagger: 0.08 }, 0.25)
      .from(".hero__disc", { scale: 0.4, autoAlpha: 0, duration: 1.4 }, 0)
      .from(".hero__products .product:first-child", { scale: 0.2, rotation: -140, autoAlpha: 0, duration: 1.5, ease: "back.out(1.4)" }, 0.15)
      .from(".hero__ring", { rotation: -90, autoAlpha: 0, duration: 1.6 }, 0.1)
      .from(".fl", { scale: 0, autoAlpha: 0, duration: 1, stagger: 0.05, ease: "back.out(2)" }, 0.5)
      .from(".hero__meta, .hero__scroll", { autoAlpha: 0, y: 20, duration: 0.8 }, 0.7)
      .from(".nav", { yPercent: -150, duration: 1, clearProps: "transform" }, 0.2);
    return tl;
  };

  const loader = $(".loader");
  if (reduced) {
    loader.remove();
  } else {
    document.body.classList.add("is-loading");
    lenis && lenis.stop();
    const counter = { v: 0 };
    const num = $(".loader__num");
    gsap.timeline()
      .to(".loader__tiles span", { y: 0, rotation: 0, opacity: 1, duration: 0.9, stagger: 0.07, ease: "back.out(1.6)" })
      .to(counter, { v: 100, duration: 1.3, ease: "power2.inOut", onUpdate: () => (num.textContent = Math.round(counter.v)) }, 0)
      .to(".loader__tiles span", { yPercent: -140, rotation: -6, duration: 0.6, stagger: 0.05, ease: "power3.in" }, "+=0.15")
      .to(".loader__count", { autoAlpha: 0, duration: 0.3 }, "<")
      .to(loader, { clipPath: "inset(0 0 100% 0)", duration: 0.9, ease: "expo.inOut" }, "-=0.25")
      .add(() => {
        loader.remove();
        document.body.classList.remove("is-loading");
        lenis && lenis.start();
      })
      .add(heroIntro(), "-=0.7");
  }

  /* ---------------------------------------------------------
     HERO — pinned scroll: products swap as you scroll
     --------------------------------------------------------- */
  const products = $$(".hero__products .product");
  const words = $$(".hero__bigword-track span");
  const listItems = $$(".hero__list li");
  const countCur = $(".hero__count-cur");
  const heroBg = ["#866DAF", "#9C5A2C", "#B83C2B", "#5E4590", "#2B2236", "#3F7D2A"];
  const steps = products.length - 1;

  if (!reduced) {
    const setActive = (i) => {
      listItems.forEach((li, k) => li.classList.toggle("is-active", k === i));
      countCur.textContent = String(i + 1).padStart(2, "0");
    };
    let lastIdx = 0;

    const htl = gsap.timeline({
      defaults: { ease: "power2.inOut" },
      scrollTrigger: {
        trigger: ".hero__stage",
        start: "top top",
        end: () => "+=" + innerHeight * steps * 0.9,
        pin: true,
        refreshPriority: 3, // pins refresh first, top to bottom, so later triggers include their spacing
        scrub: 0.8,
        snap: { snapTo: "labels", inertia: false, duration: { min: 0.25, max: 0.8 }, delay: 0.12, ease: "power2.inOut" },
        onUpdate: (self) => {
          const i = Math.round(self.progress * steps);
          if (i !== lastIdx) { lastIdx = i; setActive(i); }
        },
      },
    });
    htl.addLabel("p0", 0);
    for (let i = 1; i <= steps; i++) {
      const at = i - 1;
      const dir = i % 2 ? 1 : -1;
      htl
        .to(products[i - 1], { rotation: 120 * dir, scale: 0.25, xPercent: 70 * dir, yPercent: -50, autoAlpha: 0, duration: 1 }, at)
        .fromTo(products[i], { rotation: -120 * dir, scale: 0.25, xPercent: -70 * dir, yPercent: 50, autoAlpha: 0 },
          { rotation: 0, scale: 1, xPercent: 0, yPercent: 0, autoAlpha: 1, duration: 1, ease: "back.out(1.2)" }, at)
        .to(words[i - 1], { yPercent: -40, opacity: 0, duration: 0.6 }, at)
        .fromTo(words[i], { yPercent: 40, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 0.6 }, at + 0.4)
        .to(".hero", { backgroundColor: heroBg[i], duration: 1, ease: "none" }, at)
        .to(".hero__disc", { scale: 0.88, duration: 0.5, yoyo: true, repeat: 1, ease: "sine.inOut" }, at)
        .addLabel("p" + i, at + 1);
    }
    htl.to(".hero__ring", { rotation: 360, duration: steps, ease: "none" }, 0);
    $$(".fl").forEach((fl, k) => {
      htl.to(fl, {
        y: (k % 2 ? -1 : 1) * (60 + k * 18),
        rotation: (k % 2 ? 1 : -1) * (180 + k * 40),
        duration: steps, ease: "none",
      }, 0);
    });

    // idle floating for ingredients
    $$(".fl").forEach((fl, k) => {
      gsap.to(fl.firstElementChild || fl, {
        y: "+=" + (8 + (k % 3) * 5), x: "+=" + (k % 2 ? 6 : -6),
        duration: 2.2 + k * 0.25, ease: "sine.inOut", yoyo: true, repeat: -1,
      });
    });
  }

  /* ---------------------------------------------------------
     Marquee — infinite, speeds up & skews with scroll velocity
     --------------------------------------------------------- */
  const mRow = $(".marquee__row");
  const mInner = $(".marquee__inner");
  mRow.appendChild(mInner.cloneNode(true));
  if (!reduced) {
    const loop = gsap.to(".marquee__inner", { xPercent: -100, duration: 28, ease: "none", repeat: -1 });
    const skewTo = gsap.quickTo(".marquee__inner", "skewX", { duration: 0.4, ease: "power3" });
    ScrollTrigger.create({
      start: 0, end: "max",
      onUpdate: (self) => {
        const v = self.getVelocity();
        const boost = gsap.utils.clamp(-1, 1, v / 2500);
        gsap.to(loop, { timeScale: (self.direction === -1 ? -1 : 1) * (1 + Math.abs(boost) * 4), duration: 0.2, overwrite: true });
        skewTo(-boost * 10);
        gsap.delayedCall(0.15, () => skewTo(0));
      },
    });
  }

  if (reduced) return navCurrent(); // everything below is decorative motion

  /* ---------------------------------------------------------
     Generic reveals
     --------------------------------------------------------- */
  $$(".split-words").forEach((el) => {
    gsap.to($$(".w", el), {
      opacity: 1, stagger: 0.08, ease: "none",
      scrollTrigger: { trigger: el, start: "top 82%", end: "bottom 45%", scrub: true },
    });
  });

  $$(".split-lines").forEach((el) => {
    gsap.from($$(".wi", el), {
      yPercent: 110, rotation: 4, duration: 1, stagger: 0.04, ease: "expo.out",
      scrollTrigger: { trigger: el, start: "top 85%" },
    });
  });

  ScrollTrigger.batch(".reveal", {
    start: "top 88%",
    onEnter: (els) => gsap.fromTo(els, { y: 50, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 1, stagger: 0.1, ease: "expo.out" }),
  });
  gsap.set(".reveal", { autoAlpha: 0 });

  $$(".kicker").forEach((k) => {
    // kickers sit at the top of their section; trigger off the section so ones inside pinned areas fire on time
    gsap.from(k, { x: -30, autoAlpha: 0, duration: 0.8, ease: "expo.out", scrollTrigger: { trigger: k.closest("section") || k, start: "top 75%" } });
  });

  /* ---------------------------------------------------------
     Stats count-up + unit size squares
     --------------------------------------------------------- */
  $$(".stat__num").forEach((el) => {
    const end = +el.dataset.count;
    const plain = el.hasAttribute("data-plain");
    const suffix = el.dataset.suffix || "";
    const o = { v: plain ? 1900 : 0 };
    gsap.to(o, {
      v: end, duration: 2, ease: "power3.out",
      scrollTrigger: { trigger: el, start: "top 88%" },
      onUpdate: () => {
        const n = Math.round(o.v);
        el.innerHTML = (plain ? String(n) : n.toLocaleString("en-GB")) + (suffix.trim().length > 1 ? `<small>${suffix}</small>` : suffix);
      },
    });
  });

  gsap.from(".unit i", {
    scale: 0, duration: 1.1, stagger: 0.18, ease: "back.out(1.6)",
    scrollTrigger: { trigger: ".units", start: "top 85%" },
  });

  /* ---------------------------------------------------------
     Products — pinned horizontal scroll (desktop)
     --------------------------------------------------------- */
  const mm = gsap.matchMedia();
  mm.add("(min-width: 861px)", () => {
    const track = $(".products__track");
    const dist = () => Math.max(0, track.scrollWidth - innerWidth);
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: ".products__pin", start: "top top", end: () => "+=" + dist(),
        pin: true, scrub: 0.6, invalidateOnRefresh: true, refreshPriority: 2,
      },
    });
    tl.to(track, { x: () => -dist(), ease: "none" });
    $$(".pcard__art svg", track).forEach((svg, k) => {
      gsap.fromTo(svg, { rotation: -25 + (k % 2) * 50 }, {
        rotation: 0, ease: "none",
        scrollTrigger: { trigger: svg.closest(".pcard"), containerAnimation: tl, start: "left right", end: "center center", scrub: true },
      });
    });
  });
  gsap.fromTo(".pcard", { y: 120, rotation: (i) => (i % 2 ? 6 : -6), autoAlpha: 0 }, {
    y: 0, rotation: 0, autoAlpha: 1, duration: 1.2, stagger: 0.08, ease: "expo.out",
    scrollTrigger: { trigger: ".products", start: "top 60%" },
  });

  /* ---------------------------------------------------------
     Sandwich bars — triangles spin with scroll, steam rises
     --------------------------------------------------------- */
  gsap.to(".tri", {
    rotation: (i) => [40, 220, -60][i], ease: "none",
    scrollTrigger: { trigger: ".bars__visual", start: "top bottom", end: "bottom top", scrub: 1 },
  });
  gsap.fromTo(".bars__cup", { y: 60 }, {
    y: -40, ease: "none",
    scrollTrigger: { trigger: ".bars__visual", start: "top bottom", end: "bottom top", scrub: 1 },
  });
  gsap.fromTo(".steam", { strokeDasharray: 40, strokeDashoffset: 80 }, { strokeDashoffset: 0, duration: 1.8, repeat: -1, ease: "none" });

  gsap.from(".food__chips span", {
    scale: 0, rotation: () => gsap.utils.random(-20, 20), duration: 0.8, stagger: 0.07, ease: "back.out(2)",
    scrollTrigger: { trigger: ".food__chips", start: "top 88%" },
  });

  /* ---------------------------------------------------------
     Factory — exploded burger, layers map to production areas
     --------------------------------------------------------- */
  const layerItems = $$(".layers li");
  const explode = (pinIt) => {
    const tl = gsap.timeline({
      defaults: { ease: "power2.inOut" },
      scrollTrigger: {
        trigger: pinIt ? ".factory__pin" : ".factory__art",
        start: pinIt ? "top top" : "top 75%",
        end: pinIt ? "+=180%" : "bottom 20%",
        pin: pinIt, scrub: 0.8, refreshPriority: 1,
        onUpdate: (self) => {
          const p = self.progress;
          layerItems.forEach((li, k) => li.classList.toggle("is-on", p >= 0.08 + k * 0.22));
        },
      },
    });
    tl.to(".xl--top", { y: -130, rotation: -6, x: -14 }, 0)
      .to(".xl--lettuce", { y: -82, rotation: 4, x: 18 }, 0)
      .to(".xl--tomato", { y: -42, rotation: -3, x: -10 }, 0)
      .to(".xl--cheese", { y: -6, rotation: 5, x: 14 }, 0)
      .to(".xl--patty", { y: 30, rotation: -2 }, 0)
      .to(".xl--bottom", { y: 66, rotation: 3 }, 0)
      .to(".xl--shadow", { y: 72, scaleX: 1.2, transformOrigin: "50% 50%", opacity: 0.6 }, 0)
      .fromTo(".factory__badge", { rotation: -40, scale: 0.6 }, { rotation: -12, scale: 1 }, 0)
      .to({}, { duration: 0.25 });
    gsap.set(".xl", { transformOrigin: "50% 50%" });
  };
  mm.add("(min-width: 901px)", () => explode(true));
  mm.add("(max-width: 900px)", () => explode(false));

  /* ---------------------------------------------------------
     Hygiene checklist — ticks draw in
     --------------------------------------------------------- */
  ScrollTrigger.batch(".checks li", {
    start: "top 88%",
    onEnter: (els) => {
      gsap.fromTo(els, { x: 60, autoAlpha: 0 }, { x: 0, autoAlpha: 1, duration: 0.9, stagger: 0.12, ease: "expo.out" });
      els.forEach((el, k) => setTimeout(() => el.classList.add("is-in"), k * 120));
    },
  });

  /* ---------------------------------------------------------
     Stores — route line draws, station filter
     --------------------------------------------------------- */
  const line = $(".route__line");
  if (line) {
    const len = line.getTotalLength();
    gsap.set(line, { strokeDasharray: len, strokeDashoffset: len });
    gsap.to(line, {
      strokeDashoffset: 0, ease: "none",
      scrollTrigger: { trigger: ".route", start: "top 85%", end: "bottom 40%", scrub: 1 },
    });
  }
  gsap.from(".route__stop", {
    scale: 0, transformOrigin: "50% 50%", duration: 0.7, stagger: 0.12, ease: "back.out(2.5)",
    scrollTrigger: { trigger: ".route", start: "top 75%" },
  });
  gsap.from(".station", {
    y: 30, autoAlpha: 0, duration: 0.8, stagger: 0.06, ease: "back.out(1.8)",
    scrollTrigger: { trigger: ".stations", start: "top 90%" },
  });
  ScrollTrigger.batch(".store", {
    start: "top 92%",
    onEnter: (els) => gsap.fromTo(els, { y: 60, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.9, stagger: 0.06, ease: "expo.out" }),
  });

  const stores = $$(".store");
  $$(".station").forEach((btn) => {
    btn.addEventListener("click", () => {
      const area = btn.dataset.area;
      $$(".station").forEach((b) => {
        b.classList.toggle("is-active", b === btn);
        b.setAttribute("aria-selected", String(b === btn));
      });
      const show = stores.filter((s) => area === "all" || s.dataset.area === area);
      stores.forEach((s) => s.classList.toggle("is-hidden", !show.includes(s)));
      gsap.fromTo(show, { y: 30, autoAlpha: 0, scale: 0.96 }, { y: 0, autoAlpha: 1, scale: 1, duration: 0.6, stagger: 0.05, ease: "expo.out" });
      ScrollTrigger.refresh();
    });
  });

  /* ---------------------------------------------------------
     Gallery — rows slide in opposite directions
     --------------------------------------------------------- */
  $$(".gallery__row").forEach((row) => {
    const dir = +row.dataset.dir;
    gsap.fromTo(row, { xPercent: dir > 0 ? -18 : 0 }, {
      xPercent: dir > 0 ? 0 : -18, ease: "none",
      scrollTrigger: { trigger: ".gallery__rows", start: "top bottom", end: "bottom top", scrub: 1 },
    });
  });

  /* ---------------------------------------------------------
     Contact + footer
     --------------------------------------------------------- */
  gsap.from(".contact__phone .c", {
    yPercent: 110, rotation: 8, duration: 1, stagger: 0.035, ease: "expo.out",
    scrollTrigger: { trigger: ".contact__phone", start: "top 88%" },
  });
  gsap.from(".footer__logo span", {
    yPercent: 100, rotation: (i) => (i % 2 ? 10 : -10), duration: 1.2, stagger: 0.07, ease: "back.out(1.4)",
    scrollTrigger: { trigger: ".footer__logo", start: "top 95%" },
  });

  navCurrent();
  ScrollTrigger.sort();
  ScrollTrigger.refresh();
  addEventListener("load", () => ScrollTrigger.refresh());
  document.fonts && document.fonts.ready.then(() => ScrollTrigger.refresh());
})();
