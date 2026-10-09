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
     3D sprites — Blender turntables packed as WebP sprite sheets.
     Each .sprite[data-seq] shows a poster first, then swaps to its sheet
     when near the viewport. Frames are driven by idle spin, hover, scroll
     and drag (with momentum). Phones and low-memory devices get the smaller
     "-sm" sheets (256 px frames, about a third of the decoded memory).
     --------------------------------------------------------- */
  const SPRITE_DIR = "assets/3d/";
  const smallSheets = matchMedia("(max-width: 860px)").matches || (navigator.deviceMemory || 8) <= 4;
  const Sprites = (() => {
    const list = [];
    let manifest = null;
    const ready = fetch(SPRITE_DIR + "manifest.json").then((r) => r.json()).then((m) => (manifest = m)).catch(() => null);
    const load = (sp) => {
      if (sp.loading || !manifest || !manifest[sp.seq]) return;
      sp.loading = true;
      const meta = manifest[sp.seq];
      const img = new Image();
      img.decoding = "async";
      img.onload = () => {
        sp.meta = meta;
        sp.el.style.backgroundImage = `url(${img.src})`;
        sp.el.style.backgroundSize = `${meta.cols * 100}% ${meta.rows * 100}%`;
        sp.el.classList.add("is-sheet");
        sp.last = -1;
        draw(sp);
      };
      img.src = SPRITE_DIR + sp.seq + (smallSheets && meta.sm ? "-sm" : "") + ".webp";
    };
    const draw = (sp) => {
      if (!sp.meta) return;
      const n = sp.meta.frames;
      const f = ((Math.floor(sp.t + sp.extra + sp.drag) % n) + n) % n;
      if (f === sp.last) return;
      sp.last = f;
      const c = f % sp.meta.cols, r = Math.floor(f / sp.meta.cols);
      sp.el.style.backgroundPosition = `${(c / (sp.meta.cols - 1)) * 100}% ${(r / Math.max(1, sp.meta.rows - 1)) * 100}%`;
    };
    // the five hidden hero products wait for the page load, so the first product's sheet goes first
    const pageLoaded = new Promise((res) => {
      if (document.readyState === "complete") res();
      else addEventListener("load", () => setTimeout(res, 400));
    });
    const io = "IntersectionObserver" in window ? new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        const sp = e.target._sprite;
        sp.visible = e.isIntersecting;
        if (!e.isIntersecting) return;
        const deferred = e.target.closest(".hero__products .product:not(:first-child)");
        (deferred ? Promise.all([ready, pageLoaded]) : ready).then(() => load(sp));
      });
    }, { rootMargin: "600px 0px" }) : null;
    $$(".sprite[data-seq]").forEach((el, k) => {
      const sp = { el, seq: el.dataset.seq, t: (k * 7) % 40, extra: 0, drag: 0, vel: 0, speed: 6, boost: 1, visible: !io, last: -1 };
      el._sprite = sp;
      list.push(sp);
      const host = el.closest(".pcard, .gtile, .bars__cup");
      if (host) {
        host.addEventListener("pointerenter", () => (sp.boost = 5));
        host.addEventListener("pointerleave", () => (sp.boost = 1));
      }
      if (io) io.observe(el);
      else ready.then(() => load(sp));
    });
    return {
      list,
      get: (el) => el && el._sprite,
      tick(dt) {
        for (const sp of list) {
          if (!sp.visible || !sp.meta) continue;
          sp.t += dt * sp.speed * sp.boost;
          if (sp.vel && !sp.grabbed) {
            sp.drag += sp.vel * dt;
            sp.vel *= Math.pow(0.05, dt); // momentum decays over ~1 s
            if (Math.abs(sp.vel) < 0.5) sp.vel = 0;
          }
          draw(sp);
        }
      },
      draw,
      /* Drag horizontally on `host` to turn the 3D object. `pick` returns the sprite
         to turn (the hero swaps products). Touch drags only where `touch` is set,
         so swipe-scrolling a card row keeps working on phones. */
      draggable(host, pick, { touch = false } = {}) {
        let sp = null, lastX = 0, lastT = 0;
        host.classList.add("is-draggable");
        if (touch) host.style.touchAction = "pan-y";
        host.addEventListener("pointerdown", (e) => {
          if (e.pointerType === "touch" && !touch) return;
          if (e.button > 0) return;
          sp = pick();
          if (!sp || !sp.meta) return;
          sp.grabbed = true;
          sp.vel = 0;
          lastX = e.clientX;
          lastT = performance.now();
          host.setPointerCapture(e.pointerId);
          host.classList.add("is-grabbing");
          e.preventDefault();
        });
        host.addEventListener("pointermove", (e) => {
          if (!sp || !sp.grabbed) return;
          const now = performance.now();
          const df = -(e.clientX - lastX) / 7; // ~7 px per frame, 40 frames per turn
          sp.drag += df;
          sp.vel = gsap.utils.clamp(-120, 120, (df / Math.max(8, now - lastT)) * 1000);
          lastX = e.clientX;
          lastT = now;
          draw(sp);
        });
        const end = () => {
          if (!sp) return;
          sp.grabbed = false;
          sp = null;
          host.classList.remove("is-grabbing");
        };
        host.addEventListener("pointerup", end);
        host.addEventListener("pointercancel", end);
        host.addEventListener("lostpointercapture", end);
      },
    };
  })();

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
    $$("[data-cursor], .pcard, .gtile, .store, .bars__cup").forEach((el) => {
      el.addEventListener("pointerenter", () => {
        cursor.classList.add("is-big");
        label.textContent = el.dataset.cursor || (el.classList.contains("store") ? "Visit" : "Drag");
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
    const heroSprites = products.map((p) => Sprites.get($(".sprite", p)));
    Sprites.draggable($(".hero__plate"), () => heroSprites[lastIdx], { touch: true });

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
          // scrolling spins the 3D products: one full turn per product
          heroSprites.forEach((sp) => sp && (sp.extra = self.progress * steps * 40));
        },
      },
    });
    htl.addLabel("p0", 0);
    for (let i = 1; i <= steps; i++) {
      const at = i - 1;
      const dir = i % 2 ? 1 : -1;
      htl
        .to(products[i - 1], { rotation: 45 * dir, scale: 0.3, xPercent: 70 * dir, yPercent: -50, autoAlpha: 0, duration: 1 }, at)
        .fromTo(products[i], { rotation: -45 * dir, scale: 0.3, xPercent: -70 * dir, yPercent: 50, autoAlpha: 0 },
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

    // idle floating for the 3D shapes + glass chips
    $$(".chip").forEach((c, k) => {
      // phones: both chips drift up so the lower one never slides over the headline
      htl.to(c, { y: () => (innerWidth > 900 ? (k ? 1 : -1) * 120 : -40), duration: steps, ease: "none" }, 0);
      gsap.to(c, { yPercent: k ? 18 : -18, duration: 2.6 + k * 0.4, ease: "sine.inOut", yoyo: true, repeat: -1 });
    });
    $$(".fl").forEach((fl, k) => {
      gsap.to(fl, {
        yPercent: (k % 2 ? -1 : 1) * (14 + (k % 3) * 6), xPercent: k % 2 ? 8 : -8,
        duration: 2.2 + k * 0.25, ease: "sine.inOut", yoyo: true, repeat: -1,
      });
    });
  }

  if (!reduced) {
    gsap.ticker.add((time, dt) => Sprites.tick(Math.min(dt, 64) / 1000));
    $$(".pcard, .gtile, .bars__cup").forEach((host) => {
      const sp = Sprites.get($(".sprite", host));
      if (sp) Sprites.draggable(host, () => sp);
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
    const cardSprites = $$(".pcard .sprite", track).map(Sprites.get);
    tl.eventCallback("onUpdate", () => cardSprites.forEach((sp) => sp && (sp.extra = tl.progress() * 80)));
  });
  gsap.fromTo(".pcard", { y: 120, rotation: (i) => (i % 2 ? 6 : -6), autoAlpha: 0 }, {
    y: 0, rotation: 0, autoAlpha: 1, duration: 1.2, stagger: 0.08, ease: "expo.out",
    scrollTrigger: { trigger: ".products", start: "top 60%" },
  });

  /* ---------------------------------------------------------
     Full range — sticky 3D stage swaps product as each row passes,
     with a mouse-driven tilt
     --------------------------------------------------------- */
  const rangeItems = $$(".range__item");
  const stageImgs = $(".range__imgs");
  if (stageImgs && rangeItems.length) {
    const imgs = rangeItems.map((li) => {
      const im = document.createElement("img");
      im.alt = "";
      im.loading = "lazy";
      im.src = li.dataset.img;
      stageImgs.appendChild(im);
      return im;
    });
    const counter = $(".range__counter b");
    let cur = -1;
    const show = (i) => {
      if (i === cur) return;
      const prev = imgs[cur];
      const dir = i > cur ? 1 : -1;
      cur = i;
      rangeItems.forEach((li, k) => li.classList.toggle("is-active", k === i));
      counter.textContent = String(i + 7).padStart(2, "0");
      if (prev) gsap.to(prev, { autoAlpha: 0, scale: 0.6, rotation: -25 * dir, yPercent: -20 * dir, duration: 0.5, ease: "power3.in", onComplete: () => prev.classList.remove("is-on") });
      imgs[i].classList.add("is-on");
      gsap.fromTo(imgs[i], { autoAlpha: 0, scale: 0.6, rotation: 25 * dir, yPercent: 20 * dir },
        { autoAlpha: 1, scale: 1, rotation: 0, yPercent: 0, duration: 0.8, ease: "back.out(1.6)", overwrite: true });
    };
    rangeItems.forEach((li, k) => {
      ScrollTrigger.create({ trigger: li, start: "top 55%", end: "bottom 55%", onToggle: (self) => self.isActive && show(k) });
      li.addEventListener("pointerenter", () => finePointer && show(k));
    });
    show(0);
    if (finePointer) {
      const stage = $(".range__stage");
      const rx = gsap.quickTo(stageImgs, "rotationX", { duration: 0.6, ease: "power3" });
      const ry = gsap.quickTo(stageImgs, "rotationY", { duration: 0.6, ease: "power3" });
      $(".range").addEventListener("pointermove", (e) => {
        const r = stage.getBoundingClientRect();
        ry(((e.clientX - (r.left + r.width / 2)) / r.width) * 24);
        rx(-((e.clientY - (r.top + r.height / 2)) / r.height) * 18);
      });
    }
    gsap.to(".range__disc", { rotation: 90, scale: 1.06, ease: "none", scrollTrigger: { trigger: ".range", start: "top bottom", end: "bottom top", scrub: 1 } });
  }

  /* ---------------------------------------------------------
     Sandwich bars — triangles spin with scroll, steam rises
     --------------------------------------------------------- */
  gsap.to(".tri", {
    rotation: (i) => [40, 220, -60][i], ease: "none",
    scrollTrigger: { trigger: ".bars__visual", start: "top bottom", end: "bottom top", scrub: 1 },
  });
  const cupSprite = Sprites.get($(".bars__cup .sprite"));
  if (cupSprite) cupSprite.speed = 4;
  gsap.fromTo(".bars__cup", { y: 60 }, {
    y: -40, ease: "none",
    scrollTrigger: {
      trigger: ".bars__visual", start: "top bottom", end: "bottom top", scrub: 1,
      onUpdate: (self) => cupSprite && (cupSprite.extra = self.progress * 40),
    },
  });
  gsap.fromTo(".steam path", { strokeDasharray: 40, strokeDashoffset: 80 }, { strokeDashoffset: 0, duration: 1.8, repeat: -1, ease: "none" });

  gsap.from(".food__chips span", {
    scale: 0, rotation: () => gsap.utils.random(-20, 20), duration: 0.8, stagger: 0.07, ease: "back.out(2)",
    scrollTrigger: { trigger: ".food__chips", start: "top 88%" },
  });

  /* ---------------------------------------------------------
     Factory — exploded burger, layers map to production areas
     --------------------------------------------------------- */
  const layerItems = $$(".layers li");
  const xSprite = Sprites.get($(".sprite--explode"));
  if (xSprite) { xSprite.speed = 0; xSprite.t = 0; } // scroll-driven only
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
    // frames 0 → 39 of the Blender render: the burger flies apart as you scroll
    const frame = { f: 0 };
    tl.to(frame, {
      f: 39, ease: "none", duration: 1,
      onUpdate: () => { if (xSprite) { xSprite.t = frame.f; Sprites.draw(xSprite); } },
    }, 0)
      .fromTo(".factory__badge", { rotation: -40, scale: 0.6 }, { rotation: -12, scale: 1, duration: 1 }, 0)
      .to({}, { duration: 0.25 });
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
  gsap.from(".footer__logo img", {
    yPercent: 30, scale: 0.92, autoAlpha: 0, duration: 1.4, ease: "expo.out",
    scrollTrigger: { trigger: ".footer__logo", start: "top 95%" },
  });

  navCurrent();
  ScrollTrigger.sort();
  ScrollTrigger.refresh();
  addEventListener("load", () => ScrollTrigger.refresh());
  document.fonts && document.fonts.ready.then(() => ScrollTrigger.refresh());
})();
