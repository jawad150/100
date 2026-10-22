/* SOURCE: privacy-config.js */
/* Approved integrations only. Empty arrays mean no optional tracker is installed.
   Do not place API keys here. Update version after a material purpose/provider change.
   Optional script entries: {id, src, category:'analytics'|'marketing', cookies:[names]}.
   Scripts must be registered here, not inserted outside the loader. */
window.GRP_PRIVACY_CONFIG = Object.freeze({version:'2026-10-15-v1',retentionDays:180,scripts:[]});
;
/* SOURCE: site-quality.js */
/* Local diagnostics only. No cookies, network analytics, or personal field values. */
(() => {
 'use strict';
 const allowed=new Set(['enquiry_open','enquiry_start','enquiry_invalid','enquiry_attempt','enquiry_preview','enquiry_success','enquiry_error','newsletter_preview','newsletter_success','phone_click','plan_click']);
 const records=[];
 function emit(name,detail={}){
  if(!allowed.has(name))return;
  const safe={event:name,page:document.body.dataset.pageId||'unknown',service:typeof detail.service==='string'?detail.service.slice(0,50):undefined,plan:typeof detail.plan==='string'?detail.plan.slice(0,40):undefined};
  records.push(safe);if(records.length>50)records.shift();
  document.dispatchEvent(new CustomEvent('grp:conversion',{detail:Object.freeze(safe)}));
 }
 window.GRP_METRICS=Object.freeze({emit,read:()=>records.map(x=>({...x}))});
 const form=document.getElementById('audit-form'),dialog=document.getElementById('audit-dialog');
 if(form&&dialog){
  let started=false;
  new MutationObserver(()=>{if(dialog.open){started=false;emit('enquiry_open',{service:form.elements.service?.value,plan:form.elements.selected_plan?.value});}}).observe(dialog,{attributes:true,attributeFilter:['open']});
  form.addEventListener('input',()=>{if(!started){started=true;emit('enquiry_start');}},{passive:true});
 }
 document.addEventListener('click',e=>{
  const link=e.target.closest('a[href^="tel:"]');if(link)emit('phone_click');
  const plan=e.target.closest('[data-plan-explore]');if(plan)emit('plan_click',{plan:plan.dataset.planExplore});
 });
 document.querySelectorAll('img:not([alt])').forEach(i=>i.alt='');
})();
;
/* SOURCE: script.js */
/* No analytics, remote form endpoint, fictitious countdown or local storage. */
'use strict';
(() => {
  const $ = (query, root = document) => root.querySelector(query);
  const $$ = (query, root = document) => [...root.querySelectorAll(query)];
  const nav = $('#primary-navigation');
  const menu = $('.menu-toggle');
  const audit = $('#audit-dialog');
  const info = $('#information-dialog');
  const form = $('#audit-form');
  let lastTrigger = null;
  const closeMenu = () => {
    nav.classList.remove('is-open');
    menu.setAttribute('aria-expanded', 'false');
    menu.setAttribute('aria-label', 'Open navigation');
  };
  menu.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  });
  $$('.navigation a, .navigation button').forEach(link => link.addEventListener('click', closeMenu));
  document.addEventListener('click', e => {
    if (!nav.contains(e.target) && !menu.contains(e.target)) closeMenu();
  });
  $('.announcement-close').addEventListener('click', () => { $('.announcement').hidden = true; });
  const showDialog = (dialog, trigger) => {
    lastTrigger = trigger || document.activeElement;
    $$('dialog[open]').forEach(d => d.close());
    closeMenu();
    dialog.showModal();
    document.body.classList.add('modal-open');
  };
  $$('dialog').forEach(dialog => {
    if (dialog === audit || dialog.matches('.cs-sample-dialog,.cs-image-dialog')) return; // The minimal enquiry handles its own close and focus.
    $('[data-close]', dialog).addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', e => {
      const r = dialog.getBoundingClientRect();
      if (e.target === dialog && (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom)) dialog.close();
    });
    dialog.addEventListener('close', () => {
      if (!$('dialog[open]')) { document.body.classList.remove('modal-open'); if(lastTrigger?.isConnected&&!lastTrigger.closest('[inert]'))lastTrigger.focus({preventScroll:true}); }
    });
  });
  // Enquiry opening is delegated to enquiry-experience.js on both pages.
  const descriptions = {
    seo: {title:'SEO Services', text:'Help the right people find your business through organic search. A search brief can cover your website’s technical foundations, the questions your customers ask, and the pages that need to turn visits into enquiries.'},
    ai: {title:'AI SEO Services', text:'Make your website’s information clear, useful and easy to understand in an evolving search landscape. A brief can cover content, technical access and how your expertise is presented. Visibility or inclusion in any AI-generated answer is not guaranteed.'},
    ads: {title:'Google Ads', text:'Build an advertising brief around your customers, their searches and the action you want them to take. Discuss campaign structure, landing pages, conversion measurement and a budget appropriate to your business.'},
    local: {title:'Local SEO', text:'Help nearby customers understand what you offer and where you work. A brief can cover your business profile, service-area pages, local information and the journey from finding your business to making an enquiry.'}
  };
  const showInfo = (title, content, trigger) => {
    $('#information-title').textContent = title;
    $('#information-content').replaceChildren();
    $('#information-content').append(content);
    showDialog(info, trigger);
  };
  // Let the results section reuse the existing accessible information dialog.
  document.addEventListener('grp:information', e => {
    const detail = e.detail;
    if (!detail || !(detail.content instanceof Node)) return;
    showInfo(String(detail.title || 'Case study'), detail.content, detail.trigger);
  });
  $$('[data-service]').forEach(button => button.addEventListener('click', () => {
    const service = descriptions[button.dataset.service];
    form.elements.service.value = service.title;
    const p = document.createElement('p'); p.textContent = service.text;
    showInfo(service.title, p, button);
  }));
  $('[data-how]')?.addEventListener('click', e => {
    const steps = document.createElement('ol');
    [
      ['Tell us about your business.', 'Share your website, your audience and the goal you want search to support.'],
      ['Discuss your search priorities.', 'Explore SEO, AI SEO, Google Ads and Local SEO in the context of your business.'],
      ['Agree the next step.', 'Confirm scope, reporting, costs and responsibilities before any work begins.']
    ].forEach(([title, text]) => {
      const li = document.createElement('li'); const strong = document.createElement('strong');
      strong.textContent = title; li.append(strong, document.createTextNode(' ' + text)); steps.append(li);
    });
    showInfo('See How It Works', steps, e.currentTarget);
  });
  $$('[data-about]').forEach(button => button.addEventListener('click', e => {
    const p = document.createElement('p');
    p.textContent = 'Google Ranker Pro is a UK-based business offering SEO Services, AI SEO Services, Google Ads and Local SEO. This is an independent service-provider website preview; it does not represent Google or imply an official affiliation.';
    showInfo('About Google Ranker Pro', p, e.currentTarget);
 }));
  // The minimal single-step form is handled by enquiry-experience.js.
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });
})();
;
/* SOURCE: second-section.js */
/* Native disclosure rows work without JavaScript. This script keeps one open
   and synchronises the editable, illustrative playbook. No network calls. */
'use strict';
(() => {
  const section = document.querySelector('#why-choose-us');
  if (!section) return;
  const rows = [...section.querySelectorAll('.why-reason')];
  const plans = {
    search: { number: '01 / 04', title: 'One connected search strategy.', tasks: ['Show up in the right searches', 'Give customers a reason to choose you', 'Make the next step easy'], footer: 'Visibility with a business purpose.' },
    insight: { number: '02 / 04', title: 'Focus on the right opportunities.', tasks: ['Review your website and competitors', 'Identify the gaps worth addressing', 'Prioritise the most useful next steps'], footer: 'A direction informed by your business.' },
    market: { number: '03 / 04', title: 'Your market. Your growth plan.', tasks: ['Understand your audience and locations', 'Match the plan to your business model', 'Connect search intent with your offer'], footer: 'Built around your customers in the UK.' },
    reporting: { number: '04 / 04', title: 'Clarity at every step.', tasks: ['See the work completed', 'Review search visibility and enquiries', 'Know what comes next and why'], footer: 'Useful reporting. Clear priorities.' }
  };
  const title = section.querySelector('#note-title');
  const tasks = section.querySelector('#note-tasks');
  const counter = section.querySelector('#note-counter');
  const footer = section.querySelector('#note-footer');
  const templateIcon = tasks.querySelector('svg').cloneNode(true);
  const sync = row => {
    const plan = plans[row.dataset.reason];
    if (!plan) return;
    title.textContent = plan.title;
    counter.textContent = plan.number;
    footer.textContent = plan.footer;
    tasks.replaceChildren(...plan.tasks.map(task => {
      const line = document.createElement('span');
      line.append(templateIcon.cloneNode(true), document.createTextNode(' ' + task));
      return line;
    }));
  };
  rows.forEach(row => row.addEventListener('toggle', () => {
    if (!row.open) return;
    rows.forEach(other => { if (other !== row) other.open = false; });
    sync(row);
  }));
})();
;
/* SOURCE: case-studies-content.js */
/* Replace illustrative entries only with approved client assets and verified data. */
window.GRP_CASE_STUDIES = {
  "showExamples": true,
  "featuredId": "redesign",
  "projects": [
    {
      "id": "redesign",
      "kind": "internal",
      "name": "Google Ranker Pro",
      "sector": "In-house website design",
      "service": "SEO Services",
      "filters": [
        "website"
      ],
      "icon": "fa-magnifying-glass-chart",
      "viewBox": "0 0 512 512",
      "logo": "assets/logo-original.png",
      "headline": "One brand. A clearer path to enquiry.",
      "subheading": "Our own website, redesigned around the next step.",
      "challenge": "The earlier concept needed a stronger connection to the brand and a clearer route from browsing services to making an enquiry.",
      "work": "We brought back the original identity, simplified the enquiry journey and introduced five speaking-presenter service videos.",
      "projectLabel": "Website experience",
      "status": "Our own redesign · project screenshots",
      "period": "Earlier concept to current approved direction",
      "source": "Screenshots from this Google Ranker Pro design project. This is a design comparison, not a claim of improved business performance.",
      "before": "assets/proof/design-earlier.webp",
      "after": "assets/proof/design-current.webp",
      "beforeLabel": "Earlier concept",
      "afterLabel": "Approved direction",
      "metrics": [
        {
          "value": "Original identity",
          "label": "Your supplied logo and palette",
          "icon": "fa-check"
        },
        {
          "value": "Clearer next steps",
          "label": "Service-led enquiry buttons",
          "icon": "fa-angle-right"
        },
        {
          "value": "5 service videos",
          "label": "Muted previews, sound on click",
          "icon": "fa-play"
        }
      ],
      "approach": [
        "Retain the original supplied logo and the blue-and-orange identity.",
        "Separate the headline and artwork into responsive hero columns.",
        "Use service-specific buttons and an editable enquiry draft.",
        "Connect five clearly disclosed AI-presenter videos to the rotating gallery."
      ],
      "goal": "A clearer website and enquiry journey",
      "evidence": "The actual earlier design and current homepage screenshots are shown together. No post-launch rankings, revenue or conversion results have been supplied."
    },
    {
      "id": "law",
      "name": "London law firm",
      "sector": "Legal services",
      "service": "Local SEO",
      "filters": [
        "local",
        "service"
      ],
      "icon": "fa-scale-balanced",
      "viewBox": "0 0 640 512",
      "headline": "From Page 3 to No.1",
      "subheading": "For a London-based law firm",
      "description": "An example local SEO project: clearer service pages, an improved business profile and a simpler path from search to enquiry.",
      "metrics": [
        {
          "value": "+320%",
          "label": "Website traffic"
        },
        {
          "value": "+185%",
          "label": "Phone enquiries"
        },
        {
          "value": "#1",
          "label": "Key local keywords"
        }
      ],
      "teaser": "+320% traffic",
      "chartTitle": "Organic Traffic Growth",
      "growth": "+320%",
      "unit": "visitors",
      "values": [
        1629,
        2398,
        3190,
        4205,
        5426,
        6842
      ],
      "max": 8000,
      "currency": false,
      "approach": [
        "Review the website and local search presence.",
        "Improve service pages and business-profile information.",
        "Measure relevant searches and the journey to an enquiry."
      ],
      "goal": "More relevant local enquiries",
      "evidence": "Search Console and analytics date ranges, call-tracking attribution, keyword locations and written client approval.",
      "kind": "example",
      "period": "January–June · illustrative period",
      "source": "Sample data for design review. Not a client report.",
      "projectLabel": "Illustrative sector brief",
      "challenge": "An example local SEO project: clearer service pages, an improved business profile and a simpler path from search to enquiry.",
      "work": "Review the website and local search presence. Improve service pages and business-profile information.",
      "status": "Illustrative example · not verified client results"
    },
    {
      "id": "restaurant",
      "name": "Restaurant group",
      "sector": "Food & hospitality",
      "service": "Google Ads",
      "filters": [
        "local",
        "ads"
      ],
      "icon": "fa-utensils",
      "viewBox": "0 0 448 512",
      "headline": "More orders. Better visibility.",
      "subheading": "For a growing restaurant group",
      "description": "An example campaign connecting nearby diners with clear menus, useful location pages and a direct route to an order or reservation.",
      "metrics": [
        {
          "value": "+280%",
          "label": "Online orders"
        },
        {
          "value": "+165%",
          "label": "Table enquiries"
        },
        {
          "value": "3.8×",
          "label": "Order volume"
        }
      ],
      "teaser": "+280% orders",
      "chartTitle": "Online Order Growth",
      "growth": "+280%",
      "unit": "orders",
      "values": [
        100,
        150,
        205,
        230,
        318,
        380
      ],
      "max": 500,
      "currency": false,
      "approach": [
        "Define the local audience and dining occasions.",
        "Connect relevant advertising with focused menu and booking pages.",
        "Measure orders and reservations, not just clicks."
      ],
      "goal": "More orders and table reservations",
      "evidence": "Ordering-platform reports, booking records, paid-media spend, the comparison period and written client approval.",
      "kind": "example",
      "period": "January–June · illustrative period",
      "source": "Sample data for design review. Not a client report.",
      "projectLabel": "Illustrative sector brief",
      "challenge": "An example campaign connecting nearby diners with clear menus, useful location pages and a direct route to an order or reservation.",
      "work": "Define the local audience and dining occasions. Connect relevant advertising with focused menu and booking pages.",
      "status": "Illustrative example · not verified client results"
    },
    {
      "id": "dental",
      "name": "Dental practice",
      "sector": "Healthcare services",
      "service": "Local SEO",
      "filters": [
        "local",
        "service"
      ],
      "icon": "fa-tooth",
      "viewBox": "0 0 448 512",
      "headline": "Be found by the right patients.",
      "subheading": "For an independent dental practice",
      "description": "An example of bringing treatment information, local visibility and appointment enquiries into one clearly measured search plan.",
      "metrics": [
        {
          "value": "+410%",
          "label": "Patient enquiries"
        },
        {
          "value": "+190%",
          "label": "Local visibility"
        },
        {
          "value": "5.1×",
          "label": "Enquiry volume"
        }
      ],
      "teaser": "+410% enquiries",
      "chartTitle": "Patient Enquiry Growth",
      "growth": "+410%",
      "unit": "enquiries",
      "values": [
        40,
        67,
        103,
        133,
        165,
        204
      ],
      "max": 250,
      "currency": false,
      "approach": [
        "Review treatment-page clarity and local business information.",
        "Improve the route from a treatment search to an appointment enquiry.",
        "Track attributable enquiries while respecting patient privacy."
      ],
      "goal": "More relevant appointment enquiries",
      "evidence": "Aggregated enquiry reports, attribution rules, dates, local search measurements and written client approval. Do not include patient data.",
      "kind": "example",
      "period": "January–June · illustrative period",
      "source": "Sample data for design review. Not a client report.",
      "projectLabel": "Illustrative sector brief",
      "challenge": "An example of bringing treatment information, local visibility and appointment enquiries into one clearly measured search plan.",
      "work": "Review treatment-page clarity and local business information. Improve the route from a treatment search to an appointment enquiry.",
      "status": "Illustrative example · not verified client results"
    },
    {
      "id": "fitness",
      "name": "Fitness studio",
      "sector": "Fitness & wellbeing",
      "service": "Google Ads",
      "filters": [
        "ads",
        "service"
      ],
      "icon": "fa-dumbbell",
      "viewBox": "0 0 640 512",
      "headline": "Turn searches into new starts.",
      "subheading": "For a local fitness studio",
      "description": "An example of pairing a clear introductory offer with relevant local searches and a straightforward membership-enquiry journey.",
      "metrics": [
        {
          "value": "+230%",
          "label": "Membership leads"
        },
        {
          "value": "+145%",
          "label": "Trial bookings"
        },
        {
          "value": "3.3×",
          "label": "Enquiry volume"
        }
      ],
      "teaser": "+230% memberships",
      "chartTitle": "Membership Lead Growth",
      "growth": "+230%",
      "unit": "leads",
      "values": [
        30,
        39,
        51,
        66,
        81,
        99
      ],
      "max": 125,
      "currency": false,
      "approach": [
        "Define the audience, offer and service area.",
        "Align search advertising with the trial-booking page.",
        "Measure enquiries, trial attendance and membership outcomes separately."
      ],
      "goal": "More qualified membership enquiries",
      "evidence": "Lead records, trial bookings, membership outcomes, ad spend, attribution dates and written client approval.",
      "kind": "example",
      "period": "January–June · illustrative period",
      "source": "Sample data for design review. Not a client report.",
      "projectLabel": "Illustrative sector brief",
      "challenge": "An example of pairing a clear introductory offer with relevant local searches and a straightforward membership-enquiry journey.",
      "work": "Define the audience, offer and service area. Align search advertising with the trial-booking page.",
      "status": "Illustrative example · not verified client results"
    },
    {
      "id": "ecommerce",
      "name": "Online retailer",
      "sector": "eCommerce",
      "service": "SEO Services",
      "filters": [
        "ecommerce"
      ],
      "icon": "fa-cart-shopping",
      "viewBox": "0 0 576 512",
      "headline": "Make every product easier to find.",
      "subheading": "For a UK eCommerce brand",
      "description": "An example of improving product discovery through clearer category pages, helpful product content and a measured route from search to sale.",
      "metrics": [
        {
          "value": "+310%",
          "label": "Organic revenue"
        },
        {
          "value": "+170%",
          "label": "Product visits"
        },
        {
          "value": "4.1×",
          "label": "Revenue volume"
        }
      ],
      "teaser": "+310% revenue",
      "chartTitle": "Organic Revenue Growth",
      "growth": "+310%",
      "unit": "revenue",
      "values": [
        10000,
        14500,
        20900,
        27800,
        33750,
        41000
      ],
      "max": 50000,
      "currency": true,
      "approach": [
        "Review product discovery, category structure and technical access.",
        "Improve the information shoppers need before making a decision.",
        "Measure attributed revenue alongside returns and marketing costs."
      ],
      "goal": "More revenue from organic search",
      "evidence": "eCommerce analytics, net revenue and return definitions, attribution settings, comparison dates and written client approval.",
      "kind": "example",
      "period": "January–June · illustrative period",
      "source": "Sample data for design review. Not a client report.",
      "projectLabel": "Illustrative sector brief",
      "challenge": "An example of improving product discovery through clearer category pages, helpful product content and a measured route from search to sale.",
      "work": "Review product discovery, category structure and technical access. Improve the information shoppers need before making a decision.",
      "status": "Illustrative example · not verified client results"
    }
  ]
};
;
/* SOURCE: case-feature.js */
/* Featured case studies: one two-column panel, synced controls and latest-request
 * transitions. No analytics, fictitious live metrics or automatic case switching. */
'use strict';
(() => {
  const root = document.getElementById('business-results');
  if (!root || !window.GRP_CASE_STUDIES) return;
  const config = window.GRP_CASE_STUDIES;
  const projects = config.projects.filter(p => config.showExamples || p.kind !== 'example');
  if (!projects.length) { root.hidden = true; return; }
  const $ = s => root.querySelector(s);
  const $$ = s => [...root.querySelectorAll(s)];
  const escape = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const icon = id => `<svg class="grp-icon fa-icon" aria-hidden="true" focusable="false"><use href="#${escape(id)}"></use></svg>`;
  const mediaURL = value => {
    const text=String(value||'');
    return /^(?:assets\/|https:\/\/|data:image\/(?:png|jpeg|webp);base64,)/.test(text)?text:'';
  };
  const panel=$('#feature-project'), visual=$('#feature-visual');
  const motion=matchMedia('(prefers-reduced-motion: reduce)');
  let active=projects.find(p=>p.id===config.featuredId)||projects[0];
  let currentFilter='all', intended={id:active.id,filter:'all',direction:1};
  let pending=null, busy=false, sequence=0;
  const visible = filter => projects.filter(p=>filter==='all'||p.filters.includes(filter));
  const setText=(id,value)=>$(id).textContent=value||'';
  const valueText=(v,p)=>`${p.currency?'£':''}${Number(v).toLocaleString('en-GB')}`;
  const comparisonHTML=p=>`<div class="cf-comparison">
    <div class="cf-browser-bar"><span class="cf-browser-dots" aria-hidden="true"><i></i><i></i><i></i></span><span>Website design · internal project</span>${icon('fa-magnifying-glass-chart')}</div>
    <div class="cf-comparison-frame" style="--split:50%">
      <img src="${escape(mediaURL(p.after))}" alt="${escape(p.name)} — current approved website direction" width="1440" height="960" draggable="false">
      <img class="cf-comparison-before" src="${escape(mediaURL(p.before))}" alt="${escape(p.name)} — earlier website concept" width="1440" height="900" draggable="false">
      <span class="cf-image-caption before">${escape(p.beforeLabel)}</span><span class="cf-image-caption after">${escape(p.afterLabel)}</span>
      <div class="cf-comparison-divider" aria-hidden="true"><span>${icon('fa-angle-right')}${icon('fa-angle-right')}</span></div>
      <input class="cf-comparison-range" type="range" min="0" max="100" step="1" value="50" aria-label="Reveal the earlier or current website design" aria-valuetext="50 percent earlier concept, 50 percent current design">
    </div>
    <div class="cf-comparison-tools"><span class="cf-drag-hint">${icon('fa-angle-right')}Drag to compare</span><div class="cf-comparison-presets" aria-label="Comparison position"><button type="button" data-cf-split="100" aria-pressed="false">Before</button><button type="button" data-cf-split="50" aria-pressed="true">50 / 50</button><button type="button" data-cf-split="0" aria-pressed="false">After</button></div></div>
  </div>`;
  function bindComparison(parent) {
    parent.querySelectorAll('.cf-comparison').forEach(component=>{
      const frame=component.querySelector('.cf-comparison-frame');
      const input=component.querySelector('.cf-comparison-range');
      const set=v=>{
        const val=Math.max(0,Math.min(100,Number(v)));
        frame.style.setProperty('--split',`${val}%`);input.value=String(val);
        input.setAttribute('aria-valuetext',`${val} percent earlier concept, ${100-val} percent current design`);
        component.querySelectorAll('[data-cf-split]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.cfSplit)===val)));
      };
      input.addEventListener('input',()=>set(input.value));
      component.querySelectorAll('[data-cf-split]').forEach(b=>b.addEventListener('click',()=>set(b.dataset.cfSplit)));
    });
  }
  function chartHTML(p) {
    const max=p.max||Math.max(...p.values)*1.15, months=['Jan','Feb','Mar','Apr','May','Jun'];
    const coords=p.values.map((v,i)=>[44+i*80,208-v/max*163]);
    const path=coords.map(([x,y],i)=>`${i?'L':'M'}${x},${y.toFixed(2)}`).join(' ');
    const grid=Array.from({length:5},(_,i)=>{
      const val=max*i/4,y=208-i*40.75;
      return `<line x1="44" y1="${y}" x2="444" y2="${y}" stroke="#e5edf5"/><text x="36" y="${y+4}" text-anchor="end">${val>=1000?(val/1000)+'k':val}</text>`;
    }).join('');
    return `<div class="cf-example-chart"><div class="cf-chart-head"><h5>${escape(p.chartTitle)}</h5><span>ILLUSTRATIVE DATA</span></div>
    <div class="cf-chart-baselines"><div><small>Example baseline · January</small><strong>${valueText(p.values[0],p)}</strong></div><div><small>Example month six · June</small><strong>${valueText(p.values[5],p)}</strong></div></div>
    <div class="cf-chart-wrap"><svg viewBox="0 0 480 260" role="img" aria-label="${escape(p.chartTitle)}. Sample numbers only, not verified client results."><g>${grid}</g><path d="${path} L444,208 L44,208 Z" fill="#3fa9f5" opacity=".13"/><path class="cf-plot-line" d="${path}" fill="none" stroke="#168fe0" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>${coords.map(([x,y],i)=>`<text x="${x}" y="237" text-anchor="middle">${months[i]}</text><g class="cf-chart-point" tabindex="0" role="button" data-cf-point="${i}" aria-label="${months[i]}: ${valueText(p.values[i],p)} ${escape(p.unit)}, sample value"><circle cx="${x}" cy="${y}" r="14" fill="transparent"/><circle class="cf-point-dot" cx="${x}" cy="${y}" r="4.5" fill="#168fe0" stroke="white" stroke-width="1.5"/></g>`).join('')}</svg></div>
    <div class="cf-chart-value"><span>Explore the six-month example</span><b>${months[5]} · ${valueText(p.values[5],p)} ${escape(p.unit)}</b></div></div>
    <p class="cf-evidence-gap">${icon('fa-file-lines')}Client screenshots, comparison dates and approval are required before this can be presented as a real case study.</p>`;
  }
  function bindChart(parent,p){
    const months=['January','February','March','April','May','June'];
    parent.querySelectorAll('.cf-chart-point').forEach((point,index)=>{
      const update=()=>{parent.querySelector('.cf-chart-value b').textContent=`${months[index]} · ${valueText(p.values[index],p)} ${p.unit}`;};
      point.addEventListener('mouseenter',update);point.addEventListener('focus',update);point.addEventListener('click',update);
      point.addEventListener('keydown',e=>{
        if(e.key==='Enter'||e.key===' '){e.preventDefault();update();}
        if(e.key==='ArrowLeft'||e.key==='ArrowRight'){
          e.preventDefault();const nodes=[...parent.querySelectorAll('.cf-chart-point')];nodes[(index+(e.key==='ArrowRight'?1:5))%6].focus({preventScroll:true});
        }
      });
    });
  }
  function render(p,filter,announce=true){
    active=p;currentFilter=filter;panel.dataset.kind=p.kind;panel.dataset.project=p.id;
    $('#feature-client-mark').innerHTML=p.logo?`<img src="${escape(mediaURL(p.logo))}" alt="${escape(p.name)} original logo" width="192" height="100">`:icon(p.icon);
    setText('#feature-client-name',p.name);setText('#feature-client-context',p.sector);
    setText('#feature-service',p.projectLabel==='Illustrative sector brief'?p.service:p.projectLabel);
    setText('#feature-status',p.status);setText('#feature-headline',p.headline);setText('#feature-challenge',p.challenge);setText('#feature-work',p.work);
    setText('#feature-evidence-label',p.kind==='internal'?'BEFORE & AFTER':'SAMPLE REPORTING VIEW');
    setText('#feature-evidence-title',p.kind==='internal'?'See the design change.':'The comparison, in context.');
    setText('#feature-period',p.period);setText('#feature-source',p.source);
    setText('#feature-outcome-label',p.kind==='internal'?'The design improvements':'Illustrative outcomes');
    setText('#feature-outcome-note',p.kind==='internal'?'Implemented in this preview':'Sample figures · not verified results');
    $('#feature-outcomes').innerHTML=p.metrics.map(m=>`<div class="cf-outcome">${m.icon?`<span class="cf-outcome-icon">${icon(m.icon)}</span>`:''}<div><strong>${escape(m.value)}</strong><p>${escape(m.label)}</p></div></div>`).join('');
    visual.innerHTML=p.kind==='internal'?comparisonHTML(p):chartHTML(p);
    if(p.kind==='internal')bindComparison(visual);else bindChart(visual,p);
    const filtered=visible(filter),index=filtered.findIndex(x=>x.id===p.id);
    setText('#feature-current',String(index+1).padStart(2,'0'));setText('#feature-total',String(filtered.length).padStart(2,'0'));
    setText('#feature-project-number',String(projects.indexOf(p)+1).padStart(2,'0'));
    $$('[data-case-direction]').forEach(b=>b.disabled=filtered.length<2);
    $$('[data-case-filter]').forEach(b=>{const is=b.dataset.caseFilter===filter;b.setAttribute('aria-selected',String(is));b.tabIndex=is?0:-1;});
    panel.setAttribute('aria-labelledby',`feature-tab-${filter}`);
    $$('[data-case-story]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.caseStory===p.id)));
    $('#feature-enquire').dataset.auditService=p.service;
    if(announce)setText('#feature-live',`${p.name}. ${p.kind==='example'?'Illustrative example, not verified client results.':'Internal website design project.'} Project ${index+1} of ${filtered.length}.`);
  }
  async function effect(node,frames,timing){
    if(motion.matches||typeof node.animate!=='function')return;
    const animation=node.animate(frames,{...timing,fill:'none'});
    try{await animation.finished;}catch(_){};
  }
  function request(id,filter=currentFilter,direction=1){
    if(!projects.some(p=>p.id===id))return;
    intended={id,filter,direction};pending={...intended};
    if(!busy)drain();
  }
  async function drain(){
    busy=true;panel.setAttribute('aria-busy','true');
    while(pending){
      let next=pending;pending=null;
      if(next.id===active.id){render(active,next.filter,false);continue;}
      const oldHeight=panel.getBoundingClientRect().height;
      panel.style.height=oldHeight+'px';panel.style.overflow='hidden';
      await effect(panel,[{opacity:1,transform:'translateX(0)'},{opacity:0,transform:`translateX(${-next.direction*14}px)`}],{duration:145,easing:'ease-in'});
      // Last selection wins while content is out; do not replay obsolete clicks.
      if(pending){next=pending;pending=null;}
      render(projects.find(p=>p.id===next.id),next.filter);
      panel.style.height='auto';const newHeight=panel.getBoundingClientRect().height;panel.style.height=oldHeight+'px';
      await Promise.all([
        effect(panel,[{opacity:0,transform:`translateX(${next.direction*18}px)`},{opacity:1,transform:'translateX(0)'}],{duration:340,easing:'cubic-bezier(.2,.7,.2,1)'}),
        effect(panel,[{height:oldHeight+'px'},{height:newHeight+'px'}],{duration:340,easing:'cubic-bezier(.2,.7,.2,1)'})
      ]);
      panel.style.height='';panel.style.overflow='';
      const line=visual.querySelector('.cf-plot-line');
      if(line&&!motion.matches){const len=line.getTotalLength();effect(line,[{strokeDasharray:len,strokeDashoffset:len},{strokeDasharray:len,strokeDashoffset:0}],{duration:460,easing:'ease-out'});}
    }
    busy=false;panel.removeAttribute('aria-busy');
  }
  $$('[data-case-filter]').forEach((b,i,nodes)=>{
    b.addEventListener('click',()=>{const list=visible(b.dataset.caseFilter);if(list.length)request(list[0].id,b.dataset.caseFilter,1);});
    b.addEventListener('keydown',e=>{
      let next;
      if(e.key==='ArrowRight')next=(i+1)%nodes.length;else if(e.key==='ArrowLeft')next=(i+nodes.length-1)%nodes.length;else if(e.key==='Home')next=0;else if(e.key==='End')next=nodes.length-1;
      if(next!==undefined){e.preventDefault();nodes[next].focus({preventScroll:true});nodes[next].click();}
    });
  });
  $$('[data-case-direction]').forEach(b=>b.addEventListener('click',()=>{
    const d=Number(b.dataset.caseDirection),list=visible(intended.filter);if(list.length<2)return;
    const i=list.findIndex(p=>p.id===intended.id);request(list[(i+d+list.length)%list.length].id,intended.filter,d);
  }));
  $('#feature-industries').innerHTML=projects.filter(p=>p.kind==='example').map(p=>`<button type="button" class="cf-industry" aria-controls="feature-project" aria-pressed="false" data-case-story="${escape(p.id)}" aria-label="Explore the ${escape(p.sector)} illustrative brief">${icon(p.icon)}<span><strong>${escape(p.sector==='Food & hospitality'?'Restaurants':p.sector==='Healthcare services'?'Dental practices':p.sector==='Fitness & wellbeing'?'Fitness studios':p.sector)}</strong><small>${escape(p.service)} · example</small></span><span class="cf-industry-go" aria-hidden="true">${icon('fa-angle-right')}</span></button>`).join('');
  $$('[data-case-story]').forEach(b=>b.addEventListener('click',()=>request(b.dataset.caseStory,'all',projects.findIndex(p=>p.id===b.dataset.caseStory)>=projects.indexOf(active)?1:-1)));
  if(!projects.some(p=>p.kind==='example'))$('.case-feature-industry-band').hidden=true;
  function setEnquiry(p){
    const form=document.getElementById('audit-form');if(!form)return;
    if([...form.elements.service.options].some(o=>o.value===p.service))form.elements.service.value=p.service;
    const context=form.elements.project_context;
    if(context) context.value=`${p.name} · ${p.goal}`;
  }
  $('#feature-enquire').addEventListener('click',()=>setEnquiry(active),true);
  function showDetails(evidenceOnly=false,trigger){
    const p=active,content=document.createElement('div');content.className='cf-dialog-content';
    content.innerHTML=`<p class="cf-dialog-kicker">${escape(p.projectLabel)} · ${escape(p.service)}</p><p class="cf-dialog-note">${escape(p.kind==='internal'?'This is our own design project, not a client performance case study. No rankings, enquiries or revenue uplift is claimed.':'This is an illustrative brief. Figures are sample data and do not represent an actual client result.')}</p>${evidenceOnly?'':`<h3>${escape(p.headline)}</h3><p>${escape(p.challenge)}</p><h3>The work</h3><ul>${p.approach.map(x=>`<li>${escape(x)}</li>`).join('')}</ul>`}<h3>${p.kind==='internal'?'The design, side by side':'The illustrative data'}</h3>${p.kind==='internal'?comparisonHTML(p):chartHTML(p)}<h3>Evidence and context</h3><p>${escape(p.evidence)}</p><p><strong>Comparison period:</strong> ${escape(p.period)}</p><button type="button" class="cf-action-in-dialog ui-button"><span class="ui-button-label">Discuss a Similar Project</span>${icon('fa-angle-right')}</button>`;
    if(p.kind==='internal')bindComparison(content);else bindChart(content,p);
    content.querySelector('.cf-action-in-dialog').addEventListener('click',()=>{setEnquiry(p);$('#feature-enquire').click();});
    document.dispatchEvent(new CustomEvent('grp:information',{detail:{title:p.name+' · project detail',content,trigger}}));
  }
  $('#feature-details').addEventListener('click',e=>showDetails(false,e.currentTarget));
  $('#feature-expand').addEventListener('click',e=>showDetails(true,e.currentTarget));
  render(active,'all',false);
})();
;
/* SOURCE: proof-content.js */
/* Configure approved media and comparison evidence here. Demo images remain clearly labelled. */
window.GRP_PROOF_CONTENT = {
  "previewMode": true,
  "testimonials": [
    {
      "id": "service-film-1",
      "service": "SEO Services",
      "icon": "magnifying-glass-chart",
      "title": "Make your business easier to find.",
      "clientName": "",
      "business": "",
      "role": "",
      "src": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_122456_401efd7a-3f82-435b-9ec1-702862695f10.mp4",
      "previewSrc": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_122456_401efd7a-3f82-435b-9ec1-702862695f10.mp4",
      "poster": "",
      "captions": "",
      "transcript": "Your next customer is searching. Google Ranker Pro connects technical SEO, useful content and a clear website journey, helping people discover your business. Start with a focused review of your search visibility.",
      "approved": false,
      "ready": true,
      "mediaKind": "ai-presenter",
      "objectPosition": "50% 35%",
      "description": "A short introduction to SEO Services from Google Ranker Pro. Presented by a fictional AI-generated presenter, not a client review."
    },
    {
      "id": "service-film-2",
      "service": "Google Ads",
      "icon": "chart-column",
      "title": "More than just clicks.",
      "clientName": "",
      "business": "",
      "role": "",
      "src": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_124552_5a52b1fa-4850-4963-aee6-2213b7d5f8e2.mp4",
      "previewSrc": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_124552_5a52b1fa-4850-4963-aee6-2213b7d5f8e2.mp4",
      "poster": "",
      "captions": "",
      "transcript": "Google Ranker Pro plans Google Ads around useful keywords, relevant advert and clear landing pages. The focus is helping the right people take the next step.",
      "approved": false,
      "ready": true,
      "mediaKind": "ai-presenter",
      "objectPosition": "50% 35%",
      "description": "A short introduction to Google Ads from Google Ranker Pro. Presented by a fictional AI-generated presenter, not a client review."
    },
    {
      "id": "service-film-3",
      "service": "Local SEO",
      "icon": "map-location-dot",
      "title": "Be found closer to home.",
      "clientName": "",
      "business": "",
      "role": "",
      "src": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_122456_16e797c7-b351-4bd3-97e4-c95ea3add921.mp4",
      "previewSrc": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_122456_16e797c7-b351-4bd3-97e4-c95ea3add921.mp4",
      "poster": "",
      "captions": "",
      "transcript": "When someone searches nearby, make your business easier to find. Google Ranker Pro helps improve your business profile, local website content, and the path to an enquiry. Build visibility in the places you serve.",
      "approved": false,
      "ready": true,
      "mediaKind": "ai-presenter",
      "objectPosition": "50% 35%",
      "description": "A short introduction to Local SEO from Google Ranker Pro. Presented by a fictional AI-generated presenter, not a client review."
    },
    {
      "id": "service-film-4",
      "service": "AI SEO Services",
      "icon": "comments",
      "title": "Clarity for a changing search world.",
      "clientName": "",
      "business": "",
      "role": "",
      "src": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_122457_c113ec53-609b-4b96-bfd3-142b408afa73.mp4",
      "previewSrc": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_122457_c113ec53-609b-4b96-bfd3-142b408afa73.mp4",
      "poster": "",
      "captions": "",
      "transcript": "Search is changing, but useful information still matters. Google Ranker Pro combines strong SEO foundations with clear, well-structured content for AI-assisted discovery. Make your services easier to understand without promises of guaranteed rankings.",
      "approved": false,
      "ready": true,
      "mediaKind": "ai-presenter",
      "objectPosition": "50% 35%",
      "description": "A short introduction to AI SEO Services from Google Ranker Pro. Presented by a fictional AI-generated presenter, not a client review."
    },
    {
      "id": "service-film-5",
      "service": "Meta Ads",
      "icon": "chart-pie",
      "title": "Give your creative a clear purpose.",
      "clientName": "",
      "business": "",
      "role": "",
      "src": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_124552_105b0de4-0b05-4b22-a814-4df81d31a3cc.mp4",
      "previewSrc": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_124552_105b0de4-0b05-4b22-a814-4df81d31a3cc.mp4",
      "poster": "",
      "captions": "",
      "transcript": "Google Ranker Pro creates Facebook and Instagram ads with thoughtful creative, audience research and clear tracking. Every campaign starts with understanding business and the action you need.",
      "approved": false,
      "ready": true,
      "mediaKind": "ai-presenter",
      "objectPosition": "50% 35%",
      "description": "A short introduction to Meta Ads from Google Ranker Pro. Presented by a fictional AI-generated presenter, not a client review."
    }
  ],
  "comparisons": [
    {
      "id": "website",
      "tab": "Website experience",
      "project": "Google Ranker Pro · homepage design",
      "type": "OUR OWN WEBSITE · DESIGN PREVIEW",
      "title": "A clearer first impression.",
      "intro": "Two actual design directions from this project. Compare the first impression, the brand presentation and the route to an enquiry.",
      "before": "assets/proof/design-earlier.webp",
      "after": "assets/proof/design-current.webp",
      "beforeLabel": "EARLIER CONCEPT",
      "afterLabel": "CURRENT DIRECTION",
      "note": "Design comparison only. This is not a client case study or a claim about rankings or revenue.",
      "changes": [
        [
          "A recognisable identity",
          "The original logo, blue and orange palette, and one consistent type system."
        ],
        [
          "A clearer first step",
          "Readable service choices and prominent, consistent enquiry buttons."
        ],
        [
          "A connected experience",
          "Responsive layouts that carry the same visual language from one section to the next."
        ]
      ],
      "meta": [
        [
          "Source",
          "This redesign project"
        ],
        [
          "Evidence type",
          "Design, not performance"
        ]
      ],
      "approved": false,
      "demo": true
    },
    {
      "id": "seo",
      "tab": "SEO performance",
      "project": "SEO performance · sample dashboard",
      "type": "ILLUSTRATIVE DASHBOARD · FICTIONAL DATA",
      "title": "Put progress in context.",
      "intro": "A sample organic-search dashboard showing how traffic, enquiries and keyword visibility can be compared. Both views use fictional data and the same 28-day reporting scope.",
      "before": "assets/proof/samples/seo-before.webp",
      "after": "assets/proof/samples/seo-after.webp",
      "beforeLabel": "SAMPLE BASELINE",
      "afterLabel": "SAMPLE COMPARISON",
      "note": "Illustrative sample images only. All figures and positions are fictional, not verified client results. Replace with approved evidence before publishing.",
      "changes": [
        [
          "Traffic in context",
          "Two sample traffic trends, shown on the same chart scale."
        ],
        [
          "Visibility alongside it",
          "Example search queries and their illustrative positions."
        ],
        [
          "Enquiries, not only visits",
          "Sample enquiries shown beside sessions and technical health."
        ]
      ],
      "meta": [
        [
          "Source",
          "Original demo dashboard"
        ],
        [
          "Reporting periods",
          "Example A / B · 28 days each"
        ]
      ],
      "approved": false,
      "demo": true
    },
    {
      "id": "local",
      "tab": "Local visibility",
      "project": "Local visibility · sample search grid",
      "type": "ILLUSTRATIVE SEARCH GRID · FICTIONAL DATA",
      "title": "Make local progress visible.",
      "intro": "A visual example of local visibility across the same 25-point search area. The map, query and positions are entirely illustrative, not a live ranking report.",
      "before": "assets/proof/samples/local-before.webp",
      "after": "assets/proof/samples/local-after.webp",
      "beforeLabel": "SAMPLE BASELINE",
      "afterLabel": "SAMPLE COMPARISON",
      "note": "Illustrative sample images only. All figures and positions are fictional, not verified client results. Replace with approved evidence before publishing.",
      "changes": [
        [
          "One consistent area",
          "The same sample query and grid are used in both images."
        ],
        [
          "See the distribution",
          "Coloured positions make the two example views easy to compare."
        ],
        [
          "Keep the context visible",
          "Average positions and grid coverage accompany the map."
        ]
      ],
      "meta": [
        [
          "Source",
          "Original schematic map"
        ],
        [
          "Evidence type",
          "Fictional 5 × 5 visibility grid"
        ]
      ],
      "approved": false,
      "demo": true
    },
    {
      "id": "ads",
      "tab": "Google Ads",
      "project": "Google Ads · sample campaign report",
      "type": "ILLUSTRATIVE PAID-SEARCH REPORT · FICTIONAL DATA",
      "title": "Look beyond the click.",
      "intro": "A sample campaign comparison showing spend, enquiries and cost per enquiry together. The figures are invented for this layout preview, not actual advertising results.",
      "before": "assets/proof/samples/ads-before.webp",
      "after": "assets/proof/samples/ads-after.webp",
      "beforeLabel": "SAMPLE BASELINE",
      "afterLabel": "SAMPLE COMPARISON",
      "note": "Illustrative sample images only. All figures and positions are fictional, not verified client results. Replace with approved evidence before publishing.",
      "changes": [
        [
          "Show the spend",
          "Both sample periods use the same £1,500 advertising budget."
        ],
        [
          "Define the conversion",
          "The same example enquiry-form action is used in both views."
        ],
        [
          "Compare the full picture",
          "Sample campaign totals sit alongside the daily enquiry chart."
        ]
      ],
      "meta": [
        [
          "Source",
          "Original demo campaign report"
        ],
        [
          "Reporting periods",
          "Example A / B · 28 days each"
        ]
      ],
      "approved": false,
      "demo": true
    }
  ],
  "galleryTransition": 1050,
  "galleryStart": 0,
  "galleryBackground": "",
  "galleryBackgroundNote": "Optional approved office/background photo. Not an endorsement.",
  "galleryMode": "continuous",
  "galleryStepDuration": 7200,
  "galleryUsePosterBackdrop": false,
  "galleryPlacement": "after-audit-before-case-studies",
  "videoAdminMode": false
};
;
/* SOURCE: client-proof.js */
/* Google Ranker Pro — client film gallery and before/after viewer.
 * No framework, analytics or uploads. The lightweight preview streams the service videos. Local files remain
 * object URLs in this tab. Production media is configured in proof-content.js.
 */
'use strict';
(() => {
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => Array.from(root.querySelectorAll(s));
  const config = window.GRP_PROOF_CONTENT || {};
  const preview = config.previewMode !== false;
  const videoAdmin = config.videoAdminMode === true;
  const isPresenter = f => f?.mediaKind === "ai-presenter";
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const viewport = $('#film-viewport');
  const track = $('#film-track');
  const filmDialog = $('#proof-film-dialog');
  const player = $('#proof-full-video');
  const pairDialog = $('#proof-pair-dialog');
  const largeDialog = $('#proof-large-dialog');
  const objectURLs = new Set();
  const films = (config.testimonials || []).filter(x => (isPresenter(x) && x.ready && x.src) || preview || (x.approved === true && x.src));
  const comparisons = (config.comparisons || []).filter(x => preview || (x.approved === true && x.before && x.after));
  const svg = (name, cls = '') => `<svg class="grp-icon fa-icon ${cls}" aria-hidden="true" focusable="false"><use href="#fa-${name}"></use></svg>`;
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const validURL = s => {
    if (!s || typeof s !== 'string') return '';
    const clean = s.trim();
    if (/^(https?:|blob:|data:(?:image\/|video\/|text\/vtt[;,]))/i.test(clean)) return clean;
    if (/^[a-z][a-z0-9+.-]*:/i.test(clean) || clean.startsWith('//')) return '';
    return clean;
  };
  const fileURL = f => { const u = URL.createObjectURL(f); objectURLs.add(u); return u; };
  const reduced = () => motion.matches;
  const closeOtherDialogs = except => $$('dialog[open]').forEach(d => { if (d !== except) d.close(); });
  let proofLastTrigger = null;
  const showDialog = (dialog, trigger) => {
    proofLastTrigger = trigger || document.activeElement;
    closeOtherDialogs(dialog);
    dialog.showModal();
    document.body.classList.add('modal-open');
  };
  [filmDialog,pairDialog,largeDialog].forEach(d => d.addEventListener('close', () => {
    if (!document.querySelector('dialog[open]')) document.body.classList.remove('modal-open');
    if(proofLastTrigger?.isConnected)proofLastTrigger.focus?.({preventScroll:true});
    else if(d===filmDialog) $('.fan-card.is-centre .fan-card-button')?.focus({preventScroll:true});
  }));

  // FOMO-style circular fan. There is no translating horizontal rail and no
  // horizontal scrolling. Cards travel along an arc, turning with the arc.
  let selectedFilm=0, phase=Number(config.galleryStart)||0, tween=null;
  let paused=reduced(), focused=false, inView=false, modalOpen=false;
  let keyboardMode=false, explicitMotion=false;
  let lastFrame=0, idle=0, videoTick=0, frameId=0, dirty=true, activeIndex=-1;
  let cardWidth=300, orbitRadius=930, orbitAngle=22, totalCards=0, pointer=null;
  let suppressClickUntil=0, announceAtEnd=false, focusCentreAfterMove=false;
  const videoNodes=[], cardNodes=[];
  const pauseButton=$('#film-motion'), dots=$('#fan-dots'), backdrop=$('#fan-backdrop-image');
  const stepDuration=Math.max(4000, Number(config.galleryStepDuration)||7200);
  const motionAllowed=()=>!paused&&(!reduced()||explicitMotion);
  const duration=Math.max(600, Math.min(1800, Number(config.galleryTransition)||1150));
  const modulo=(n,m)=>((n%m)+m)%m;
  const angularDistance=(a,b,n)=>modulo(a-b+n/2,n)-n/2;
  const fullyBlocked=()=>document.hidden||modalOpen||!!document.querySelector('dialog[open]');
  const isWritten=()=>false; // This gallery now accepts real recordings, not text-review animations.
  const localName=f=>isPresenter(f)?f.service:(f.clientName||(f.src?'Your client video':'Client story'));
  function pauseLabel(){
    pauseButton.setAttribute('aria-pressed',String(paused));
    pauseButton.setAttribute('aria-label',paused?'Resume the rotating gallery':'Pause the rotating gallery');
    pauseButton.lastElementChild.textContent=paused?'Resume rotation':'Pause rotation';
    pauseButton.title=paused?'Resume the rotating gallery':'Pause the rotating gallery';
  }
  function filmMarkup(f,i,physical){
    const src=validURL(f.src),loopSrc=validURL(f.previewSrc)||src,poster=validURL(f.poster);
    const title=isPresenter(f)?(f.title||f.service):(f.clientName||(src?'Your client’s story':f.service+' review'));
    const written=false;
    return `<article class="fan-card ${src?'has-video':''}" data-film-card="${i}" data-orbit-index="${physical}" data-palette="${i%5}" data-media-kind="${esc(f.mediaKind||'client-recording')}">
      <button class="fan-card-button" type="button" data-film-open="${i}" tabindex="-1" aria-haspopup="dialog" aria-controls="proof-film-dialog" aria-label="${esc(src?'Watch '+title:'Add the client recording for '+f.service)}">
       <div class="fan-placeholder" aria-hidden="true"><span class="fan-placeholder-no">${String(i+1).padStart(2,'0')}</span>${svg('quote-left','fan-empty-quote')}<strong>${src?"Watch the service<br>explained.":"Client video<br>to be added."}</strong><small>${src?"SELECT TO PLAY WITH SOUND":"ORIGINAL RECORDING REQUIRED"}</small></div>
       ${poster?`<img class="fan-card-poster" src="${esc(poster)}" alt="" loading="lazy" draggable="false">`:''}
       ${src?`<video class="fan-loop" autoplay muted loop playsinline preload="none" data-src="${esc(loopSrc)}" style="object-position:${esc(f.objectPosition||'50% 35%')}" ${poster?`poster="${esc(poster)}"`:''} aria-hidden="true" tabindex="-1"></video>`:''}
       <span class="fan-topline"><span class="fan-index">${String(i+1).padStart(2,'0')}</span>${isPresenter(f)?'<span class="fan-ai-label">AI PRESENTER</span>':''}<span class="fan-expand">${svg('expand')}</span></span>
       <span class="fan-open-badge">${svg(src?'play':'plus')}<span>${src?(written?'Watch written review':'Watch with sound'):'Add client video'}</span></span>
       <span class="fan-caption"><span class="fan-service">${esc(f.service)}</span><strong>${esc(title)}</strong><span class="fan-caption-bottom"><span>${esc(isPresenter(f)?'AI presenter · 15 seconds':(written?'Written review · animated excerpt':(f.business||(src?'Client recording':'Client recording to be added'))))}</span>${svg('angle-right')}</span></span>
      </button></article>`;
  }
  function renderBackdrop(){
    const src=validURL(config.galleryBackground)||(config.galleryUsePosterBackdrop===false?'':validURL(films[activeIndex]?.poster));
    if(src){if(backdrop.getAttribute('src')!==src)backdrop.src=src;backdrop.hidden=false;}
    else{backdrop.hidden=true;backdrop.removeAttribute('src');}
  }
  backdrop.addEventListener('error',()=>{backdrop.hidden=true;});
  function buildRail(){
    videoNodes.forEach(v=>{v.pause();v.removeAttribute('src');v.load();});
    videoNodes.length=0;cardNodes.length=0;
    totalCards=films.length*Math.ceil(9/Math.max(films.length,1));
    track.innerHTML=Array.from({length:totalCards},(_,p)=>filmMarkup(films[p%films.length],p%films.length,p)).join('');
    cardNodes.push(...$$('.fan-card',track));videoNodes.push(...$$('video',track));
    if(dots)dots.innerHTML=films.map((f,i)=>`<button type="button" class="fan-dot" data-fan-select="${i}" aria-current="false" aria-label="Show ${esc(f.clientName||f.service)} video ${i+1}"><span></span></button>`).join('');
    videoNodes.forEach(v=>{
      v.muted=true;v.defaultMuted=true;v.volume=0;v.playsInline=true;v.loop=true;
      v.addEventListener('volumechange',()=>{if(!v.muted)v.muted=true;});
      v.addEventListener('play',()=>{if(fullyBlocked()||!motionAllowed()||!inView)v.pause();});
      v.addEventListener('error',()=>{
        v.dataset.failed='true';v.hidden=true;
        const card=v.closest('.fan-card');card.classList.add('is-failed');
        $('.fan-open-badge span',card).textContent='Video unavailable';
        $('.fan-caption-bottom>span',card).textContent='Check your internet connection';
      });
    });
    $$('img.fan-card-poster',track).forEach(img=>img.addEventListener('error',()=>img.hidden=true));
    activeIndex=-1;measureRail();layoutFan();updatePreviews();
    const connected=films.filter(f=>validURL(f.src)).length;
    // The supplementary footer has been removed. Disclosure remains above the gallery and in the film popup.
    wake();
  }
  function measureRail(){
    if(!cardNodes.length)return;
    cardWidth=cardNodes[0].offsetWidth;
    orbitRadius=cardWidth*(viewport.clientWidth<=760?3.34:3.12);
    orbitAngle=viewport.clientWidth<=760?20:22;
    dirty=true;layoutFan();wake();
  }
  function layoutFan(){
    if(!totalCards)return;
    for(const card of cardNodes){
      const d=angularDistance(Number(card.dataset.orbitIndex),phase,totalCards);
      const a=d*orbitAngle,theta=a*Math.PI/180;
      const visible=Math.abs(d)<3.4;
      card.style.visibility=visible?'visible':'hidden';
      card.style.pointerEvents=visible?'auto':'none';
      if(visible){
        const x=orbitRadius*Math.sin(theta)-cardWidth/2;
        const y=orbitRadius*(1-Math.cos(theta));
        card.style.transform=`translate3d(${x.toFixed(3)}px,${y.toFixed(3)}px,0) rotate(${a.toFixed(3)}deg)`;
        card.style.opacity=String(Math.max(0,Math.min(1,(3.4-Math.abs(d))/.55)));
        card.style.zIndex=String(Math.round(1000-Math.abs(d)*120));
      }
      card.dataset.distance=d.toFixed(3);
      const centre=Math.abs(d)<.5;
      card.classList.toggle('is-centre',centre);
      const button=$('.fan-card-button',card);
      button.tabIndex=centre?0:-1;
      card.setAttribute('aria-hidden',String(!visible));
      if(centre)button.setAttribute('aria-current','true');else button.removeAttribute('aria-current');
    }
    const next=modulo(Math.round(phase),films.length);
    if(next!==activeIndex){
      activeIndex=next;
      (dots ? $$('[data-fan-select]',dots) : []).forEach((b,i)=>b.setAttribute('aria-current',String(i===next)));
      viewport.dataset.activeFilm=String(next);
      renderBackdrop();
    }
    dirty=false;
  }
  function updatePreviews(){
    for(const card of cardNodes){
      const v=$('video',card);if(!v)continue;
      const distance=Math.abs(Number(card.dataset.distance));
      const visible=inView&&distance<2.35;
      if(visible&&motionAllowed()&&!navigator.connection?.saveData&&!fullyBlocked()&&!v.getAttribute('src')&&v.dataset.failed!=='true'){
        v.muted=true;v.defaultMuted=true;v.volume=0;v.src=v.dataset.src;
      }
      const canPlay=visible&&!navigator.connection?.saveData&&!fullyBlocked()&&motionAllowed()&&v.dataset.failed!=='true';
      if(canPlay&&v.paused)v.play().then(()=>{if(fullyBlocked()||!motionAllowed()||!inView){v.pause();return;}v.closest('.fan-card')?.classList.add('is-playing');}).catch(()=>{});
      else if(!canPlay&&!v.paused)v.pause();
    }
  }
  function startTween(target,manual=false){
    idle=0;announceAtEnd=manual;
    if(reduced()){
      phase=target;tween=null;layoutFan();updatePreviews();
      if(manual)announce();
    }else tween={start:performance.now(),from:phase,to:target,duration};
    wake();
  }
  function announce(){
    $('#fan-live-status').textContent=`Story ${activeIndex+1} of ${films.length}: ${films[activeIndex]?.clientName||films[activeIndex]?.service}.`;
    if(focusCentreAfterMove){focusCentreAfterMove=false;$('.fan-card.is-centre .fan-card-button')?.focus({preventScroll:true});}
  }
  function draw(now){
    frameId=0;
    const dt=lastFrame?Math.min(now-lastFrame,70):0;lastFrame=now;
    if(tween){
      const t=Math.min(1,(now-tween.start)/tween.duration);
      // Smooth acceleration/deceleration; no abrupt replacement of card media.
      const ease=t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
      phase=tween.from+(tween.to-tween.from)*ease;
      dirty=true;
      if(t===1){phase=modulo(tween.to,totalCards);tween=null;idle=0;if(announceAtEnd)announceAtEnd='pending';}
    }else if(inView&&motionAllowed()&&!focused&&!pointer&&!fullyBlocked()){
      // Continuous clockwise travel from the very first visible frame.
      // No stationary interval; pointer hover does not stop the fan.
      phase=modulo(phase+dt/stepDuration,totalCards);
      dirty=true;
    }
    if(dirty)layoutFan();
    if(announceAtEnd==='pending'){announce();announceAtEnd=false;}
    if(++videoTick%12===0)updatePreviews();
    const needsFrames=!!tween||(inView&&motionAllowed()&&!focused&&!pointer&&!fullyBlocked());
    viewport.dataset.phase=phase.toFixed(4);
    viewport.dataset.running=String(inView&&motionAllowed()&&!focused&&!pointer&&!fullyBlocked());
    if(!document.hidden&&needsFrames&&!frameId)frameId=requestAnimationFrame(draw);
  }
  function wake(){if(!frameId&&!document.hidden){lastFrame=0;frameId=requestAnimationFrame(draw);}}
  function moveRail(direction){
    if(!films.length)return;
    const target=Math.round(tween?tween.to:phase)+(direction<0?-1:1);
    startTween(target,true);
  }
  $('#fan-intro-watch')?.addEventListener('click',event=>openFilm(activeIndex,event.currentTarget));
  pauseButton.addEventListener('click',()=>{paused=!paused;explicitMotion=!paused;focused=false;idle=0;if(paused)tween=null;pauseLabel();updatePreviews();wake();});
  $$('[data-film-direction]').forEach(b=>b.addEventListener('click',()=>moveRail(Number(b.dataset.filmDirection))));
  dots?.addEventListener('click',e=>{
    const b=e.target.closest('[data-fan-select]');if(!b)return;
    const target=Number(b.dataset.fanSelect),base=Math.round(tween?tween.to:phase);
    startTween(base+angularDistance(target,modulo(base,films.length),films.length),true);
  });
  // Hover must not freeze the loop. Keyboard users still get a stable target.
  document.addEventListener('keydown',()=>{keyboardMode=true;},true);
  document.addEventListener('pointerdown',()=>{keyboardMode=false;focused=false;wake();},true);
  viewport.addEventListener('focusin',()=>{focused=keyboardMode;});
  viewport.addEventListener('focusout',()=>setTimeout(()=>{focused=keyboardMode&&viewport.contains(document.activeElement);idle=0;wake();},0));
  viewport.addEventListener('keydown',e=>{
    if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();focusCentreAfterMove=true;moveRail(e.key==='ArrowLeft'?-1:1);}
    if(e.key==='Home'){e.preventDefault();focusCentreAfterMove=true;startTween(Math.round(phase)+angularDistance(0,modulo(Math.round(phase),films.length),films.length),true);}
  });
  track.addEventListener('click',e=>{
    if(performance.now()<suppressClickUntil){e.preventDefault();return;}
    const b=e.target.closest('[data-film-open]');if(b)openFilm(Number(b.dataset.filmOpen),b);
  });
  viewport.addEventListener('pointerdown',e=>{
    if(e.button!==0)return;
    pointer={id:e.pointerId,x:e.clientX,y:e.clientY};
  });
  viewport.addEventListener('pointerup',e=>{
    if(!pointer||pointer.id!==e.pointerId)return;
    const dx=e.clientX-pointer.x,dy=e.clientY-pointer.y;pointer=null;wake();
    if(Math.abs(dx)>40&&Math.abs(dx)>Math.abs(dy)*1.3){suppressClickUntil=performance.now()+450;moveRail(dx>0?-1:1);}
  });
  viewport.addEventListener('pointercancel',()=>{pointer=null;wake();});
  window.addEventListener('pointerup',()=>{if(pointer){pointer=null;wake();}});
  const railObserver=new IntersectionObserver(entries=>{
    inView=entries[0].isIntersecting;updatePreviews();idle=0;if(inView)wake();
  },{rootMargin:'0px',threshold:0.01});
  railObserver.observe(viewport);
  new ResizeObserver(measureRail).observe(viewport);
  document.addEventListener('visibilitychange',()=>{updatePreviews();if(!document.hidden){idle=0;wake();}});
  motion.addEventListener('change',()=>{
    if(reduced()){paused=true;explicitMotion=false;if(tween){phase=tween.to;tween=null;layoutFan();}}
    pauseLabel();updatePreviews();wake();
  });
  if(films.length){buildRail();pauseLabel();wake();}else $('#client-reviews').hidden=true;

  // Muted preview -> user-initiated modal with sound. Only this player may be audible.
  const soundButton=$('#proof-play-sound');
  function playWithSound(){
    if(!player.getAttribute('src')||!filmDialog.open)return;
    soundButton.hidden=true;
    player.defaultMuted=false;
    player.removeAttribute('muted');
    player.muted=false;player.volume=1;player.loop=false;player.playsInline=true;
    player.play().catch(error=>{
      if(error.name==='AbortError')return;
      if(filmDialog.open&&player.getAttribute('src')){
        soundButton.hidden=false;
        if(error.name==='NotAllowedError')$('#proof-film-status').textContent='Your browser needs one more click. Choose “Play with sound”.';
      }
    });
  }
  soundButton.addEventListener('click',playWithSound);
  function openFilm(index,trigger) {
    selectedFilm=index;
    const f=films[index];if(!f)return;
    modalOpen=true;updatePreviews();
    const ready=!!validURL(f.src);
    $('#proof-film-title').textContent=isPresenter(f)?f.service:(f.clientName||f.service+' · client video');
    const synthetic=isPresenter(f);
    $('#proof-film-description').textContent=synthetic ? f.description : (ready
      ? ([f.role,f.business].filter(Boolean).join(' · ')||'Watch the original recording with sound.')
      : 'Add the original recording with the client’s permission.');
    $('#proof-film-kind').innerHTML=synthetic ? '<span></span>SERVICE EXPLAINER · AI PRESENTER' : '<span></span>CLIENT VIDEO';
    $('#proof-film-meta').textContent=synthetic ? '15-second introduction · English · Sound on' : f.service;
    $('#proof-film-empty').hidden=ready;player.hidden=!ready;
    $('#proof-video-error').hidden=true;soundButton.hidden=true;
    $('#proof-transcript').hidden=!f.transcript;
    $('#proof-transcript p').textContent=f.transcript||'';
    $('#proof-film-status').textContent=synthetic
      ? 'AI-generated presenter and voice. This is a service explanation, not a customer testimonial.'
      : 'Original recording. Use the controls for sound and full screen.';
    $('.proof-upload-inline').hidden=!videoAdmin;$('#proof-video-file').hidden=!videoAdmin;
    $('#proof-client-fields').hidden=!videoAdmin||!ready||synthetic;
    filmDialog.dataset.mediaKind=f.mediaKind||'client-recording';
    $('.proof-cta',filmDialog).dataset.auditService=f.service;
    $('#proof-client-name').value=f.clientName||'';
    $('#proof-client-business').value=f.business||'';
    showDialog(filmDialog,trigger);
    player.pause();player.removeAttribute('src');player.removeAttribute('poster');player.replaceChildren();
    if(ready){
      player.src=validURL(f.src);
      if(validURL(f.poster))player.poster=validURL(f.poster);
      if(validURL(f.captions)){
        const caption=document.createElement('track');caption.kind='captions';caption.srclang='en';caption.label='English';caption.src=validURL(f.captions);caption.default=true;player.append(caption);
      }
      player.load();
      playWithSound(); // Called synchronously from the click, preserving user activation.
    }else player.load();
  }
  filmDialog.addEventListener('close',()=>{
    player.pause();player.muted=true;player.removeAttribute('src');player.removeAttribute('poster');player.load();
    soundButton.hidden=true;modalOpen=false;idle=0;updatePreviews();wake();
  });
  player.addEventListener('playing',()=>{soundButton.hidden=true;});
  player.addEventListener('loadedmetadata',()=>{
    filmDialog.dataset.orientation=player.videoWidth>player.videoHeight?'landscape':'portrait';
  });
  player.addEventListener('error',()=>{
    if(!player.getAttribute('src'))return;
    $('#proof-video-error').hidden=false;
    $('#proof-video-error').textContent='This recording could not be played. Check the path or use an H.264 MP4 with AAC audio. Your original file has not been changed.';
  });
  $('#proof-video-file').addEventListener('change',e=>{
    const file=e.target.files[0];if(!file)return;
    if(!file.type.startsWith('video/')&&!/\.(mp4|webm|mov|m4v)$/i.test(file.name)){$('#proof-film-status').textContent='Please choose a video recording.';return;}
    if(file.size>300*1024*1024){$('#proof-film-status').textContent='Choose a recording smaller than 300 MB for this browser preview.';return;}
    const index=selectedFilm,f=films[index];
    if(f.local&&objectURLs.has(f.src)){URL.revokeObjectURL(f.src);objectURLs.delete(f.src);}
    f.mediaKind='client-recording';f.transcript='';f.captions='';f.previewSrc='';f.approved=false;f.src=fileURL(file);f.poster='';f.local=true;
    buildRail();openFilm(index,null);
    $('#proof-film-status').textContent=`${file.name} · Local preview. Refreshing removes this selection.`;
    const capturedSrc=f.src;
    player.addEventListener('loadeddata',()=>{
      if(f.src!==capturedSrc)return;
      try{
        const canvas=document.createElement('canvas'),ratio=Math.min(1,720/Math.max(player.videoWidth,1));
        canvas.width=Math.round(player.videoWidth*ratio);canvas.height=Math.round(player.videoHeight*ratio);
        if(!canvas.width||!canvas.height)return;
        canvas.getContext('2d').drawImage(player,0,0,canvas.width,canvas.height);
        f.poster=canvas.toDataURL('image/jpeg',.85);
        cardNodes.filter(c=>Number(c.dataset.filmCard)===index).forEach(c=>{
          let img=$('.fan-card-poster',c);
          if(!img){img=document.createElement('img');img.className='fan-card-poster';img.alt='';$('.fan-placeholder',c).after(img);}
          img.src=f.poster;const v=$('video',c);if(v)v.poster=f.poster;
        });
        renderBackdrop();
      }catch(_){/* Poster capture is optional; playback does not depend on it. */}
    },{once:true});
    e.target.value='';
  });
  $('#proof-save-client').addEventListener('click',()=>{
    const f=films[selectedFilm];if(!f)return;
    f.clientName=$('#proof-client-name').value.trim();f.business=$('#proof-client-business').value.trim();
    $('#proof-film-title').textContent=isPresenter(f)?f.service:(f.clientName||f.service+' · client video');
    $('#proof-film-description').textContent=f.business||'Watch the original client recording with sound.';
    buildRail();$('#proof-film-status').textContent='Client details applied to this local preview only.';
  });

  // Before/after comparison: native keyboard slider and image upload previews.
  let currentComparison=0,queuedComparison=null,switching=false;
  let pendingBefore=null,pendingAfter=null;
  const split=$('#proof-split'), comparer=$('#proof-comparer'), panel=$('#proof-panel');
  function setSplit(value,animate=false) {
    value=Math.max(0,Math.min(100,Number(value)||0));
    comparer.classList.toggle('is-snapping',animate&&!reduced());
    comparer.style.setProperty('--split',value+'%');split.value=String(value);
    split.setAttribute('aria-valuetext',`${value} percent before and ${100-value} percent after`);
    $$('[data-split]').forEach(b=>{const selected=Number(b.dataset.split)===value;b.classList.toggle('is-current',selected);b.setAttribute('aria-pressed',String(selected));});
    $('#proof-before-label').style.opacity='1';
    $('#proof-after-label').style.opacity='1';
  }
  split.addEventListener('input',()=>setSplit(split.value));
  // The native input handles keyboard access. Direct pointer geometry prevents
  // thumb padding from skewing the split on small screens.
  split.addEventListener('pointerdown',e=>{
    if(e.button!==0)return;split.setPointerCapture(e.pointerId);
    const update=ev=>{const r=comparer.getBoundingClientRect();setSplit((ev.clientX-r.left)/r.width*100);};
    update(e);
    const move=ev=>update(ev),end=()=>{split.removeEventListener('pointermove',move);split.removeEventListener('pointerup',end);split.removeEventListener('pointercancel',end);};
    split.addEventListener('pointermove',move);split.addEventListener('pointerup',end);split.addEventListener('pointercancel',end);
  });
  $$('[data-split]').forEach(b=>b.addEventListener('click',()=>setSplit(b.dataset.split,true)));
  function setImage(which,src,label) {
    const image=$('#proof-'+which),layer=$('#proof-'+which+'-layer'),empty=$('.proof-image-empty',layer);
    if(validURL(src)) {image.src=validURL(src);image.alt=label;image.hidden=false;empty.hidden=true;}
    else {image.removeAttribute('src');image.hidden=true;empty.hidden=false;}
  }
  ['before','after'].forEach(which=>$('#proof-'+which).addEventListener('error',()=>{
    const img=$('#proof-'+which);if(!img.getAttribute('src'))return;img.hidden=true;
    const empty=$('.proof-image-empty',$('#proof-'+which+'-layer'));empty.hidden=false;$('span',empty).textContent='Image unavailable · choose a replacement';
  }));
  function populateComparison(index) {
    currentComparison=index;
    const c=comparisons[index];
    $('#proof-project-label').textContent=c.project;
    $('#proof-detail-tag').textContent=c.type;
    $('#proof-detail-title').textContent=c.title;
    $('#proof-detail-intro').textContent=c.intro;
    $('#proof-comparison-notice').textContent=c.note;
    $('#proof-before-label').textContent=c.beforeLabel||'BEFORE';
    $('#proof-after-label').textContent=c.afterLabel||'AFTER';
    setImage('before',c.before,c.beforeLabel+' — '+c.project);
    setImage('after',c.after,c.afterLabel+' — '+c.project);
    $('#proof-differences').innerHTML=(c.changes||[]).map(([title,body])=>`<div class="proof-difference"><span>${svg('check')}</span><div><strong>${esc(title)}</strong><p>${esc(body)}</p></div></div>`).join('');
    $('#proof-metadata').innerHTML=(c.meta||[]).map(([label,val])=>`<div><span>${esc(label)}</span><strong>${esc(val)}</strong></div>`).join('');
    $$('#proof-tabs button').forEach((b,i)=>{b.setAttribute('aria-selected',String(i===index));b.tabIndex=i===index?0:-1;});
    panel.setAttribute('aria-labelledby','proof-tab-'+c.id);
    $('#proof-expand').disabled=!c.before||!c.after;
    $('#proof-expand').title=c.before&&c.after?'Enlarge comparison':'Add a before-and-after pair first';
    setSplit(50);
    panel.dataset.comparison=c.id;
    panel.dispatchEvent(new CustomEvent('comparison:changed',{bubbles:true,detail:{id:c.id,ready:!!(c.before&&c.after)}}));
  }
  async function selectComparison(index) {
    queuedComparison=index;
    if(switching)return;
    switching=true;
    while(queuedComparison!==null) {
      const target=queuedComparison;queuedComparison=null;
      if(target===currentComparison)continue;
      if(!reduced()) await panel.animate([{opacity:1,transform:'translateY(0)'},{opacity:0,transform:'translateY(7px)'}],{duration:160,easing:'ease-in',fill:'forwards'}).finished.catch(()=>{});
      populateComparison(target);
      panel.getAnimations().forEach(a=>a.cancel());
      if(!reduced())await panel.animate([{opacity:0,transform:'translateY(12px)'},{opacity:1,transform:'translateY(0)'}],{duration:360,easing:'cubic-bezier(.2,.7,.25,1)'}).finished.catch(()=>{});
    }
    switching=false;
  }
  if(comparisons.length) {
    $('#proof-tabs').innerHTML=comparisons.map((c,i)=>`<button type="button" role="tab" id="proof-tab-${esc(c.id)}" aria-controls="proof-panel" aria-selected="${i===0}" tabindex="${i===0?0:-1}" data-proof-index="${i}">${svg(['file-lines','chart-column','map-location-dot','chart-pie'][i]||'file-lines')}<span>${esc(c.tab)}</span></button>`).join('');
    $('#proof-tabs').addEventListener('click',e=>{const b=e.target.closest('[data-proof-index]');if(b)selectComparison(Number(b.dataset.proofIndex));});
    $('#proof-tabs').addEventListener('keydown',e=>{
      const b=e.target.closest('[data-proof-index]');if(!b)return;
      let i=Number(b.dataset.proofIndex);
      if(e.key==='ArrowRight')i=(i+1)%comparisons.length;
      else if(e.key==='ArrowLeft')i=(i-1+comparisons.length)%comparisons.length;
      else if(e.key==='Home')i=0;
      else if(e.key==='End')i=comparisons.length-1;else return;
      e.preventDefault();$$('[data-proof-index]')[i].focus();selectComparison(i);
    });
    populateComparison(0);
  } else $('#before-after').hidden=true;
  $('#proof-load-pair').hidden=!preview;
  $('#proof-load-pair').addEventListener('click',e=>{
    pendingBefore=null;pendingAfter=null;
    ['before','after'].forEach(w=>{$('#proof-'+w+'-file').value='';$('#proof-'+w+'-filename').textContent='Select PNG, JPG or WebP';});
    $('#proof-pair-status').textContent='Use screenshots with the same dimensions and reporting scope.';
    showDialog(pairDialog,e.currentTarget);
  });
  ['before','after'].forEach(which=>$('#proof-'+which+'-file').addEventListener('change',e=>{
    const f=e.target.files[0];if(!f)return;
    if(!['image/png','image/jpeg','image/webp'].includes(f.type)||f.size>30*1024*1024) {$('#proof-pair-status').textContent='Select a PNG, JPG or WebP smaller than 30 MB.';return;}
    const test=new Image(),url=fileURL(f);
    test.onload=()=>{const data={url,width:test.naturalWidth,height:test.naturalHeight,name:f.name};if(which==='before')pendingBefore=data;else pendingAfter=data;$('#proof-'+which+'-filename').textContent=`${f.name} · ${data.width} × ${data.height}`;$('#proof-pair-status').textContent=pendingBefore&&pendingAfter?'Both images are ready. Select View comparison.':'Now choose the matching '+(which==='before'?'after':'before')+' image.';};
    test.onerror=()=>{$('#proof-pair-status').textContent='This image could not be read. Select a different file.';};test.src=url;
  }));
  $('#proof-apply-pair').addEventListener('click',()=>{
    if(!pendingBefore||!pendingAfter){$('#proof-pair-status').textContent='Choose both the before and the after image first.';return;}
    const c=comparisons[currentComparison];
    c.before=pendingBefore.url;c.after=pendingAfter.url;c.beforeLabel='BEFORE';c.afterLabel='AFTER';
    c.project='Your selected images · local preview';c.type='YOUR IMAGES · LOCAL PREVIEW';c.title='Your comparison, side by side.';
    c.intro='The images you selected are displayed without retouching. Add the approved project details, source and date context before publishing.';
    c.note='Local preview only. These files have not been uploaded or published. Refreshing the page removes this selection.';
    c.changes=[['Original images','Both uploaded views are displayed without edits.'],['Matched context','Confirm the reporting periods and measurement scope.'],['Clear evidence','Add the project description and approval before launch.']];
    c.meta=[['Source','Locally selected images'],['Status','Not published']];
    populateComparison(currentComparison);pairDialog.close();
    split.focus({preventScroll:true});
  });
  $('#proof-expand').addEventListener('click',e=>{
    const c=comparisons[currentComparison];if(!c?.before||!c?.after)return;
    $('#proof-large-title').textContent=c.project;$('#proof-large-note').textContent=c.note;
    $('#proof-large-before').src=validURL(c.before);$('#proof-large-after').src=validURL(c.after);
    showDialog(largeDialog,e.currentTarget);
  });
  document.addEventListener('grp:client-stories-dialog-change',()=>{updatePreviews();wake();});
  window.addEventListener('pagehide',()=>{videoNodes.forEach(v=>v.pause());player.pause();});
  // Object URLs intentionally remain valid for the lifetime of the page.
  // Browsers release them when the tab closes; no files are uploaded or stored.
})();
;
/* SOURCE: interface-refinement.js */
/* Small enhancements only. The gallery and comparison controllers remain
   in client-proof.js; no duplicate players, observers or slider controllers. */
(() => {
  'use strict';
  const panel = document.getElementById('proof-panel');
  const updateReadyState = () => {
    if (!panel) return;
    const before = document.getElementById('proof-before');
    const after = document.getElementById('proof-after');
    const ready = Boolean(before?.getAttribute('src') && after?.getAttribute('src'));
    panel.dataset.ready = String(ready);
    const slider = document.getElementById('proof-split');
    if (slider) slider.disabled = !ready;
    panel.querySelectorAll('[data-split]').forEach(button => { button.disabled = !ready; });
  };
  panel?.addEventListener('comparison:changed', updateReadyState);
  updateReadyState();

  const preloadSampleImages = () => {
    const items = window.GRP_PROOF_CONTENT?.comparisons || [];
    items.filter(item => item.demo && item.id !== 'website').forEach(item => {
      [item.before, item.after].filter(Boolean).forEach(src => {
        const image = new Image();
        image.src = src;
        image.decode?.().catch(() => {});
      });
    });
  };
  const comparisonSection = document.getElementById('before-after');
  if (comparisonSection && 'IntersectionObserver' in window) {
    const sampleObserver = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) {
        preloadSampleImages();
        sampleObserver.disconnect();
      }
    }, { rootMargin: '600px' });
    sampleObserver.observe(comparisonSection);
  } else { preloadSampleImages(); }

  // All dynamic CTAs keep the shared visual component and native semantics.
  document.querySelectorAll('.case-feature-secondary,.case-feature-band-cta').forEach(button => {
    button.classList.add('ui-button');
  });
  // Pointer and keyboard users have the same exact before / split / after states.
  document.getElementById('proof-split')?.addEventListener('keydown', event => {
    if (event.key === 'Escape') event.currentTarget.blur();
  });
})();
;
/* SOURCE: newsletter-config.js */
/* Public browser configuration. NEVER place API keys or mailing-list credentials here.
 * Keep endpoint empty during review; no email address will leave the browser.
 * In production, point this at your server-side subscribe route.
 * See FOOTER-NEWSLETTER-SETUP.md for the request / response contract.
 */
window.GRP_NEWSLETTER_CONFIG = Object.freeze({
  endpoint: "",
  timeoutMs: 15000
});
;
/* SOURCE: footer.js */
/* Isolated footer behaviour. No storage, trackers, third-party submissions or demo success. */
(() => {
  'use strict';
  const footer = document.getElementById('site-footer');
  if (!footer) return;
  footer.querySelectorAll('[data-footer-year]').forEach(node => {
    node.textContent = String(new Date().getFullYear());
  });
  footer.querySelectorAll('[data-footer-top]').forEach(link => {
    link.addEventListener('click', event => {
      event.preventDefault();
      const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
      window.scrollTo({ top: 0, behavior: reduce ? 'instant' : 'smooth' });
      const homeLink = document.querySelector('.logo-link, .brand, .logo');
      if (homeLink instanceof HTMLElement) homeLink.focus({ preventScroll: true });
    });
  });
  const form = document.getElementById('newsletter-form');
  if (!form) return;
  const fieldset = form.querySelector('fieldset');
  const email = document.getElementById('newsletter-email');
  const consent = document.getElementById('newsletter-consent');
  const status = document.getElementById('newsletter-status');
  const submit = form.querySelector('[type="submit"]');
  const submitLabel = submit.querySelector('.ui-button-label');
  const emailError = document.getElementById('newsletter-email-error');
  const consentError = document.getElementById('newsletter-consent-error');
  const company = document.getElementById('newsletter-website');
  let busy = false;
  fieldset.disabled = false;
  const clearError = (field, output) => {
    field.removeAttribute('aria-invalid');
    output.textContent = '';
    output.hidden = true;
  };
  const error = (field, output, message) => {
    field.setAttribute('aria-invalid', 'true');
    output.textContent = message;
    output.hidden = false;
  };
  const message = (state, text) => {
    status.dataset.state = state;
    status.textContent = text;
    status.hidden = false;
  };
  email.addEventListener('input', () => {clearError(email, emailError); status.hidden = true;});
  consent.addEventListener('change', () => {clearError(consent, consentError); status.hidden = true;});
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy) return;
    status.hidden = true;
    clearError(email, emailError);
    clearError(consent, consentError);
    email.value = email.value.trim();
    let valid = true;
    if (!email.value || !email.checkValidity() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
      error(email, emailError, 'Please enter a valid email address.');
      valid = false;
    }
    if (!consent.checked) {
      error(consent, consentError, 'Please confirm that you would like to receive these emails.');
      valid = false;
    }
    if (!valid) {(email.hasAttribute('aria-invalid') ? email : consent).focus(); return;}
    if (company.value.trim()) {
      message('error', 'We could not process this signup. Please refresh and try again.'); return;
    }
    const config = window.GRP_NEWSLETTER_CONFIG || {};
    if (!config.endpoint) {
      message('preview', 'Preview only: your details are valid, but the newsletter is not connected yet. Nothing has been sent and you have not been subscribed.');
      return;
    }
    let endpoint;
    try {
      endpoint = new URL(config.endpoint, location.href);
      const isLocalHTTP = endpoint.protocol === 'http:' && ['localhost', '127.0.0.1', '[::1]'].includes(endpoint.hostname);
      if (endpoint.protocol !== 'https:' && !isLocalHTTP) throw new Error('Unsafe endpoint');
    } catch {
      message('error', 'Newsletter signup is not available yet. Please try again later.'); return;
    }
    busy = true; submit.disabled = true;
    form.setAttribute('aria-busy', 'true');
    submitLabel.textContent = 'Subscribing…';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), Math.min(Math.max(Number(config.timeoutMs) || 15000, 1000), 30000));
    try {
      const headers = {'Content-Type': 'application/json', 'Accept': 'application/json'};
      const csrf = document.querySelector('meta[name="csrf-token"]')?.content;
      if (csrf) headers['X-CSRF-Token'] = csrf;
      const response = await fetch(endpoint.href, {
        method: 'POST', headers, credentials: 'same-origin', signal: controller.signal,
        body: JSON.stringify({ email: email.value, consent: true,
          consentText: 'I agree to receive marketing emails from Google Ranker Pro.',
          source: 'footer_newsletter', website: company.value })
      });
      if (response.status === 429) {
        message('error', 'Please wait a moment before trying again.'); return;
      }
      if (!response.ok) throw new Error('Request rejected');
      const data = await response.json();
      if (data.status === 'confirmation_required') {
        message('success', 'Please check your inbox and confirm your email address to finish subscribing.');
      } else if (data.status === 'subscribed') {
        message('success', 'You’re subscribed to The Search Brief. Thank you for joining us.');
      } else {throw new Error('Unconfirmed status');}
      form.reset();
    } catch (failure) {
      message('error', failure.name === 'AbortError'
        ? 'The connection timed out. Please try again in a moment.'
        : 'We could not confirm your subscription. Please try again in a moment.');
    } finally {
      clearTimeout(timeout);
      busy = false; submit.disabled = false;
      form.removeAttribute('aria-busy');
      submitLabel.textContent = 'Subscribe';
    }
  });
})();
;
/* SOURCE: pricing-content.js */
/* Rates and scope reproduced from the user's 2026 pricing guide, page 4.
 * Review-only. Do not treat VAT / setup / term as agreed. Edit this and static markup together. */
window.GRP_PLANS = [
  {
    "id": "local",
    "name": "Local SEO",
    "price": 747,
    "icon": "map-location-dot",
    "focus": "Win local enquiries",
    "tag": "YOUR LOCAL MARKET",
    "short": "For businesses that want to be found in their town, city or service area.",
    "fit": "Local service businesses",
    "scope": "Local discovery",
    "headline": "Be found where you do business.",
    "description": "A focused starting point for your local search presence, with clearer website pages and a better-supported business profile.",
    "features": [
      "Google Business Profile optimisation",
      "On-page optimisation across 5 pages",
      "2 SEO blog posts each month",
      "Monthly ranking report"
    ],
    "full": [
      "Google Business Profile optimisation",
      "Up to 10 target keywords",
      "On-page optimisation across 5 pages",
      "Local citations and directory work",
      "2 SEO blog posts per month",
      "Monthly ranking report"
    ],
    "service": "Local SEO"
  },
  {
    "id": "growth",
    "name": "Growth SEO",
    "price": 1497,
    "icon": "chart-column",
    "focus": "Grow organic reach",
    "tag": "LOCAL + NATIONAL REACH",
    "short": "For growing businesses ready for a broader, more competitive search presence.",
    "fit": "Established, growing businesses",
    "scope": "Broader organic growth",
    "headline": "Build a broader search presence.",
    "description": "A more extensive organic programme, bringing technical work, content and competitor insight together around your business priorities.",
    "features": [
      "Technical SEO and site-health fixes",
      "4 optimised content pieces each month",
      "Competitor and content-gap analysis",
      "Conversion tracking and strategy call"
    ],
    "full": [
      "Up to 30 target keywords",
      "Technical SEO and site-health fixes",
      "4 optimised content pieces per month",
      "Authority link-building activity",
      "Competitor and content-gap analysis",
      "Conversion tracking and strategy call"
    ],
    "service": "SEO Services"
  },
  {
    "id": "authority",
    "name": "Authority SEO",
    "price": 2947,
    "icon": "magnifying-glass-chart",
    "focus": "Compete at scale",
    "tag": "COMPETITIVE SEARCH MARKETS",
    "short": "For businesses with more demanding markets, deeper content needs and bigger ambitions.",
    "fit": "Competitive search markets",
    "scope": "Search authority",
    "headline": "Go deeper in competitive markets.",
    "description": "A larger programme for demanding search environments, extending the Growth scope with topic clusters, more content and dedicated strategic input.",
    "features": [
      "Everything in the Growth SEO scope",
      "8 content pieces each month",
      "AI search content optimisation",
      "Dedicated strategist; fortnightly calls"
    ],
    "full": [
      "Everything in the Growth SEO scope",
      "60+ keywords and topic clusters",
      "8 content pieces per month",
      "Digital PR and backlink activity",
      "AI Overviews / AEO optimisation",
      "Dedicated strategist and fortnightly calls"
    ],
    "service": "SEO Services"
  }
];
;
/* SOURCE: pricing.js */
/* Scoped pricing interactions. No network calls, checkout, storage or invented discounts. */
'use strict';
(() => {
  const plans = Array.isArray(window.GRP_PLANS) ? window.GRP_PLANS : [];
  const get = id => plans.find(p => p.id === id);
  const $ = s => document.querySelector(s);
  const $$ = s => Array.from(document.querySelectorAll(s));
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const fmt = n => new Intl.NumberFormat('en-GB').format(n);
  const svg = name => {
    const e = document.createElementNS('http://www.w3.org/2000/svg','svg');
    e.setAttribute('class','grp-icon fa-icon');e.setAttribute('aria-hidden','true');e.setAttribute('focusable','false');
    const use = document.createElementNS(e.namespaceURI,'use');use.setAttribute('href','#fa-'+name);e.append(use);return e;
  };
  const home = $('#plans-pricing');
  const focus = id => {
    const p=get(id);
    $$('[data-plan-card]').forEach(c=>c.classList.toggle('is-focus',!!p&&c.dataset.planCard===id));
    $$('[data-plan-focus]').forEach(b=>b.setAttribute('aria-pressed',String(!!p&&b.dataset.planFocus===id)));
    const reset=$('[data-plan-reset]');if(reset)reset.hidden=!p;
    const status=$('.pricing-focus-status');if(status)status.textContent=p?`${p.name} highlighted for ${p.focus.toLowerCase()}. All plans remain available to compare.`:'All three plans shown equally.';
  };
  $$('[data-plan-focus]').forEach(b=>b.addEventListener('click',()=>focus(b.getAttribute('aria-pressed')==='true'?'':b.dataset.planFocus)));
  $('[data-plan-reset]')?.addEventListener('click',()=>focus(''));

  // Store plan selection in dedicated fields; never overwrite the visitor's goal.
  const form=$('#audit-form'),dialog=$('#audit-dialog');
  const originalTitle=$('#audit-title')?.textContent;
  const originalIntro=dialog?.querySelector('.modal-intro')?.textContent;
  function selectForEnquiry(id){
    if(!form||!dialog)return;
    const p=get(id);const box=$('#pricing-enquiry-context');
    form.elements.selected_plan.value=p?p.name:'';
    form.elements.plan_guide_rate.value=p?`£${fmt(p.price)} per month`:'';
    if(box)box.hidden=!p;
    if(p){
      $('#pricing-enquiry-name').textContent=p.name;
      $('#pricing-enquiry-rate').textContent=`£${fmt(p.price)} / month · Guide rate; final costs and terms to be confirmed.`;
      form.elements.service.value=p.service;
    }else{
      $('#audit-title').textContent=originalTitle;
      dialog.querySelector('.modal-intro').textContent=originalIntro;
    }
  }
  // Capture runs before the existing data-audit handler opens its accessible dialog.
  document.addEventListener('click',event=>{
    const b=event.target.closest('[data-audit]');if(!b)return;
    selectForEnquiry(b.dataset.planEnquiry||'');
    if(b.hasAttribute('data-pricing-custom'))form.elements.service.value='Not sure yet';
    if(b.dataset.planEnquiry){
      const r=$('#enquiry-result');if(r)r.hidden=true;form.hidden=false;
    }
  },true);
  $('#pricing-clear-plan')?.addEventListener('click',()=>{
    selectForEnquiry('');form.elements.service.value='Not sure yet';form.querySelector('[name="name"]')?.focus({preventScroll:true});
  });
  // Changing a service manually must not leave a conflicting paid plan on the draft.
  form?.elements.service.addEventListener('change',()=>{
    const selected=plans.find(p=>p.name===form.elements.selected_plan.value);
    if(selected&&selected.service!==form.elements.service.value)selectForEnquiry('');
  });

  const panel=$('#plan-panel');
  let current='local',pending=null,busy=false;
  function setDetail(p){
    if(!panel)return;
    current=p.id;
    $('#plan-detail-kicker').textContent=p.tag;
    $('#plan-detail-heading').textContent=p.headline;
    $('#plan-detail-description').textContent=p.description;
    $('#plan-detail-name').textContent=p.name;
    $('#plan-detail-price').textContent=fmt(p.price);
    $('#plan-detail-fit').textContent=p.fit;
    $('#plan-detail-icon').replaceChildren(svg(p.icon));
    const ul=$('#plan-detail-features');ul.replaceChildren();
    p.full.forEach(text=>{const li=document.createElement('li'),span=document.createElement('span');span.textContent=text;li.append(svg('check'),span);ul.append(li);});
    const b=$('#plan-discuss');b.dataset.planEnquiry=p.id;b.querySelector('.ui-button-label').textContent='Discuss '+p.name;
    panel.setAttribute('aria-labelledby','tab-'+p.id);
    $$('[data-detail-plan]').forEach(t=>{const on=t.dataset.detailPlan===p.id;t.setAttribute('aria-selected',String(on));t.tabIndex=on?0:-1;});
    $('#pricing-detail-status').textContent=`${p.name}. Monthly guide rate £${fmt(p.price)}. ${p.full.length} scope items displayed.`;
  }
  async function animate(frames,opts){
    if(motion.matches||!panel?.animate)return;
    try{await panel.animate(frames,opts).finished;}catch{/* Cancellation is safe. */}
  }
  async function switchDetail(id,update=true){
    if(!get(id)||!panel)return;
    pending=id;
    if(busy)return;
    busy=true;panel.setAttribute('aria-busy','true');
    while(pending){
      let next=pending;pending=null;
      if(next===current)continue;
      await animate([{opacity:1,transform:'translateY(0)'},{opacity:0,transform:'translateY(7px)'}],{duration:150,easing:'ease-in',fill:'none'});
      if(pending){next=pending;pending=null;}
      setDetail(get(next));
      if(update){try{const u=new URL(location.href);if(u.protocol==='http:'||u.protocol==='https:'||u.protocol==='file:'){u.searchParams.set('plan',next);u.hash='plan-detail';history.replaceState(null,'',u);}}catch{/* file preview may restrict history. */}}
      await animate([{opacity:0,transform:'translateY(9px)'},{opacity:1,transform:'translateY(0)'}],{duration:280,easing:'cubic-bezier(.2,.65,.2,1)',fill:'none'});
    }
    panel.removeAttribute('aria-busy');busy=false;
  }
  if(panel){
    let id=window.GRP_PREVIEW_PLAN||new URLSearchParams(location.search).get('plan');
    if(location.hash.startsWith('#plan='))id=location.hash.slice(6);
    setDetail(get(id)||plans[0]);
    $$('[data-detail-plan]').forEach((b,i)=>{
      b.addEventListener('click',()=>switchDetail(b.dataset.detailPlan));
      b.addEventListener('keydown',e=>{
        const bs=$$('[data-detail-plan]');let n=i;
        if(e.key==='ArrowRight')n=(i+1)%bs.length;else if(e.key==='ArrowLeft')n=(i+bs.length-1)%bs.length;else if(e.key==='Home')n=0;else if(e.key==='End')n=bs.length-1;else return;
        e.preventDefault();bs[n].focus();switchDetail(bs[n].dataset.detailPlan);
      });
    });
    if(location.hash.startsWith('#plan='))requestAnimationFrame(()=>panel.scrollIntoView({block:'start',behavior:'instant'}));
  }
  // FAQ opens and closes with a measured content height, not an abrupt jump.
  $$('.pricing-faq').forEach(d=>{
    const summary=d.querySelector('summary'),body=d.querySelector('.pricing-faq-body');let running=null;
    summary.setAttribute('aria-expanded',String(d.open));
    summary.addEventListener('click',e=>{
      e.preventDefault();if(running)return;
      const opening=!d.open;if(opening)d.open=true;
      summary.setAttribute('aria-expanded',String(opening));
      if(motion.matches||!body.animate){d.open=opening;return;}
      const height=body.scrollHeight;
      running=body.animate(opening?[{height:'0px',opacity:0},{height:height+'px',opacity:1}]:[{height:height+'px',opacity:1},{height:'0px',opacity:0}],{duration:240,easing:'cubic-bezier(.25,.7,.25,1)'});
      running.onfinish=()=>{d.open=opening;running=null;};
      running.oncancel=()=>{running=null;};
    });
  });
})();
;
/* SOURCE: client-stories-content.js */
/* Client feedback mixed with clearly labelled AI service explainers. No invented customer recordings. */
window.GRP_CLIENT_STORIES = {
  "previewMode": true,
  "allowLocalPreview": false,
  "sourceChecked": "2026-10-13",
  "notes": "Written excerpts retain their original attribution. The five speaking videos are existing AI-generated SERVICE EXPLAINERS, not customer testimonials. Each card and popup discloses this distinction.",
  "items": [
    {
      "id": "client-film-1",
      "kind": "video",
      "service": "SEO Services",
      "name": "",
      "role": "",
      "business": "",
      "src": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_122456_401efd7a-3f82-435b-9ec1-702862695f10.mp4",
      "previewSrc": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_122456_401efd7a-3f82-435b-9ec1-702862695f10.mp4",
      "poster": "",
      "captions": "",
      "transcript": "Your next customer is searching. Google Ranker Pro connects technical SEO, useful content and a clear website journey, helping people discover your business. Start with a focused review of your search visibility.",
      "approved": false,
      "theme": "sky",
      "objectPosition": "50% 35%",
      "mediaKind": "ai-presenter",
      "title": "Make your business easier to find.",
      "description": "A short introduction to SEO Services from Google Ranker Pro. Presented by a fictional AI-generated presenter, not a client review.",
      "ready": true,
      "duration": "15 sec"
    },
    {
      "id": "written-1",
      "kind": "written",
      "name": "Marco Silva",
      "role": "E-commerce Manager",
      "service": "SEO Services",
      "quote": "They explained everything in simple terms",
      "theme": "navy",
      "sourceUrl": "https://googlerankerpro.com/",
      "approved": false,
      "sourceType": "existing-website-excerpt"
    },
    {
      "id": "client-film-2",
      "kind": "video",
      "service": "Google Ads",
      "name": "",
      "role": "",
      "business": "",
      "src": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_124552_5a52b1fa-4850-4963-aee6-2213b7d5f8e2.mp4",
      "previewSrc": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_124552_5a52b1fa-4850-4963-aee6-2213b7d5f8e2.mp4",
      "poster": "",
      "captions": "",
      "transcript": "Google Ranker Pro plans Google Ads around useful keywords, relevant advert and clear landing pages. The focus is helping the right people take the next step.",
      "approved": false,
      "theme": "warm",
      "objectPosition": "50% 35%",
      "mediaKind": "ai-presenter",
      "title": "More than just clicks.",
      "description": "A short introduction to Google Ads from Google Ranker Pro. Presented by a fictional AI-generated presenter, not a client review.",
      "ready": true,
      "duration": "15 sec"
    },
    {
      "id": "written-2",
      "kind": "written",
      "name": "Daniel Okafor",
      "role": "Sales Director",
      "service": "Google Ads",
      "quote": "responsive, knowledgeable",
      "theme": "white",
      "sourceUrl": "https://googlerankerpro.com/",
      "approved": false,
      "sourceType": "existing-website-excerpt"
    },
    {
      "id": "written-3",
      "kind": "written",
      "name": "Emily Kowalski",
      "role": "Small Business Owner",
      "service": "Website experience",
      "quote": "sleek, user-friendly, and mobile-optimised",
      "theme": "white",
      "sourceUrl": "https://googlerankerpro.com/",
      "approved": false,
      "sourceType": "existing-website-excerpt"
    },
    {
      "id": "client-film-3",
      "kind": "video",
      "service": "Local SEO",
      "name": "",
      "role": "",
      "business": "",
      "src": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_122456_16e797c7-b351-4bd3-97e4-c95ea3add921.mp4",
      "previewSrc": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_122456_16e797c7-b351-4bd3-97e4-c95ea3add921.mp4",
      "poster": "",
      "captions": "",
      "transcript": "When someone searches nearby, make your business easier to find. Google Ranker Pro helps improve your business profile, local website content, and the path to an enquiry. Build visibility in the places you serve.",
      "approved": false,
      "theme": "sky",
      "objectPosition": "50% 35%",
      "mediaKind": "ai-presenter",
      "title": "Be found closer to home.",
      "description": "A short introduction to Local SEO from Google Ranker Pro. Presented by a fictional AI-generated presenter, not a client review.",
      "ready": true,
      "duration": "15 sec"
    },
    {
      "id": "client-film-4",
      "kind": "video",
      "service": "AI SEO Services",
      "name": "",
      "role": "",
      "business": "",
      "src": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_122457_c113ec53-609b-4b96-bfd3-142b408afa73.mp4",
      "previewSrc": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_122457_c113ec53-609b-4b96-bfd3-142b408afa73.mp4",
      "poster": "",
      "captions": "",
      "transcript": "Search is changing, but useful information still matters. Google Ranker Pro combines strong SEO foundations with clear, well-structured content for AI-assisted discovery. Make your services easier to understand without promises of guaranteed rankings.",
      "approved": false,
      "theme": "warm",
      "objectPosition": "50% 35%",
      "mediaKind": "ai-presenter",
      "title": "Clarity for a changing search world.",
      "description": "A short introduction to AI SEO Services from Google Ranker Pro. Presented by a fictional AI-generated presenter, not a client review.",
      "ready": true,
      "duration": "15 sec"
    },
    {
      "id": "written-4",
      "kind": "written",
      "name": "Amina Yusuf",
      "role": "Event Planning Business Owner",
      "service": "Branding experience",
      "quote": "incredibly talented and patient",
      "theme": "blue",
      "sourceUrl": "https://googlerankerpro.com/",
      "approved": false,
      "sourceType": "existing-website-excerpt"
    },
    {
      "id": "written-5",
      "kind": "written",
      "name": "Javier Morales",
      "role": "Restaurant Manager",
      "service": "Local SEO",
      "quote": "attention to detail and dedication",
      "theme": "navy",
      "sourceUrl": "https://googlerankerpro.com/",
      "approved": false,
      "sourceType": "existing-website-excerpt"
    },
    {
      "id": "client-film-5",
      "kind": "video",
      "service": "Meta Ads",
      "name": "",
      "role": "",
      "business": "",
      "src": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_124552_105b0de4-0b05-4b22-a814-4df81d31a3cc.mp4",
      "previewSrc": "https://d8j0ntlcm91z4.cloudfront.net/user_39GMH3fFiyE1qeSboJH47Azrcrr/hf_20261012_124552_105b0de4-0b05-4b22-a814-4df81d31a3cc.mp4",
      "poster": "",
      "captions": "",
      "transcript": "Google Ranker Pro creates Facebook and Instagram ads with thoughtful creative, audience research and clear tracking. Every campaign starts with understanding business and the action you need.",
      "approved": false,
      "theme": "sky",
      "objectPosition": "50% 35%",
      "mediaKind": "ai-presenter",
      "title": "Give your creative a clear purpose.",
      "description": "A short introduction to Meta Ads from Google Ranker Pro. Presented by a fictional AI-generated presenter, not a client review.",
      "ready": true,
      "duration": "15 sec"
    }
  ]
};
;
/* SOURCE: client-stories.js */
/* Mixed client reviews: stable masonry, progressive reveal, optional genuine films.
 * Content in client-stories-content.js. No uploads, trackers or permanent storage.
 */
(() => {
  'use strict';
  const config=window.GRP_CLIENT_STORIES||{};
  const section=document.getElementById('client-stories');
  if(!section)return;
  const $=(s,r=section)=>r.querySelector(s);
  const preview=config.previewMode===true;
  const isPresenter=f=>f?.mediaKind==='ai-presenter';
  const safeUrl=value=>{
    if(typeof value!=='string'||!value.trim())return '';
    const v=value.trim();
    if(/^https?:\/\//i.test(v)||/^blob:/i.test(v)||/^data:(?:image\/|video\/|text\/vtt[;,])/i.test(v))return v;
    if(/^[a-z][a-z\d+.-]*:/i.test(v)||v.startsWith('//')||v.includes('\\'))return '';
    return v;
  };
  const items=(Array.isArray(config.items)?config.items:[]).filter(f=>
    ['written','video'].includes(f.kind)&&(preview||(isPresenter(f)&&f.ready&&safeUrl(f.src))||(f.approved===true&&(f.kind==='written'?!!f.quote:!!safeUrl(f.src))))
  ).map(f=>({...f}));
  if(!items.length){return;}
  $('#mrx-review-note').hidden=!preview;
  const grid=$('#mrx-grid'),viewport=$('#mrx-viewport'),shell=$('#mrx-shell');
  const more=$('#mrx-more'),moreText=more.querySelector('.ui-button-label');
  const note=$('#mrx-reveal-note'),live=$('#mrx-live');
  const motion=matchMedia('(prefers-reduced-motion: reduce)');
  const saveData=()=>navigator.connection?.saveData===true;
  const dialog=document.getElementById('mrx-dialog');
  const find=s=>dialog.querySelector(s);
  const player=find('#mrx-player'),sound=find('#mrx-sound'),file=find('#mrx-file');
  let selected=-1,lastTrigger=null,stage=0,fullyExpanded=false,animating=false,layoutFrame=0;
  let positions=[],fullHeight=0,revealHeight=0,finishTimer=0,columns=4;
  const cards=[],urls=new Set();
  const bounds=new Map();
  const icon=(name,cls='')=>{
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('class','grp-icon fa-icon '+cls);svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');
    const use=document.createElementNS(svg.namespaceURI,'use');use.setAttribute('href','#fa-'+name);svg.append(use);return svg;
  };
  const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=String(text);return n;};
  const initials=name=>(name||'').trim().split(/\s+/).filter(Boolean).slice(0,2).map(s=>s[0]).join('');
  function createWritten(f){
    const card=el('article','mrx-card mrx-card--written');card.dataset.theme=f.theme||'white';
    card.setAttribute('role','listitem');card.setAttribute('aria-label','Written review excerpt attributed to '+f.name);
    const top=el('div','mrx-quote-top');top.append(icon('quote-left','mrx-quote-icon'),el('span','mrx-type','WRITTEN REVIEW · EXCERPT'));
    const quote=el('blockquote','', '“'+f.quote+'”');
    const by=el('div','mrx-author'),avatar=el('span','mrx-initials',initials(f.name));avatar.setAttribute('aria-hidden','true');
    const name=el('div');name.append(el('cite','',f.name),el('small','',f.role||f.business||''));by.append(avatar,name);
    card.append(top,quote,by);return card;
  }
  function createVideo(f,index){
    const card=el('article','mrx-card mrx-card--video');card.dataset.theme=f.theme||'sky';card.setAttribute('role','listitem');
    const button=el('button','mrx-video-button');button.type='button';button.dataset.clientFilm=String(index);button.setAttribute('aria-haspopup','dialog');button.setAttribute('aria-controls','mrx-dialog');
    const art=el('div','mrx-slot-art');art.setAttribute('aria-hidden','true');art.append(el('span','mrx-slot-grid'),el('span','mrx-slot-no',String(index+1).padStart(2,'0')));
    const centre=el('span','mrx-slot-centre');centre.append(icon('quote-left'));
    const heading=el('strong');heading.append(document.createTextNode('Their story.'),document.createElement('br'),document.createTextNode('In their voice.'));
    centre.append(heading,el('small','','Space for an original client recording.'));
    const top=el('span','mrx-video-top');top.append(el('span','mrx-video-tag','VIDEO SPACE'),icon('expand'));
    const caption=el('span','mrx-video-caption'),copy=el('span','mrx-video-copy');
    copy.append(el('span','',f.service),el('strong','',f.service+' story'),el('small','','Client recording to be added'));
    const action=el('span','mrx-card-action');action.append(icon('plus'));caption.append(copy,action);
    button.append(art,centre,top,caption);card.append(button);
    updateCard(card,f,index);return card;
  }
  function updateCard(card,f,index){
    const button=card.querySelector('button');const src=safeUrl(f.src),poster=safeUrl(f.poster);
    card.classList.toggle('has-video',!!src);card.dataset.mediaKind=f.mediaKind||'client-recording';if(isPresenter(f))card.setAttribute('data-nosnippet','');
    button.setAttribute('aria-label',src?'Watch '+(isPresenter(f)?f.service+' AI service explainer':(f.name||f.service+' client video'))+' with sound':'Preview '+f.service+' client-video space');
    card.querySelector('.mrx-video-tag').textContent=src?(isPresenter(f)?'AI PRESENTER · SERVICE VIDEO':(f.local?'LOCAL PREVIEW':'CLIENT VIDEO')):'VIDEO SPACE';
    const copy=card.querySelector('.mrx-video-copy');copy.children[1].textContent=src?(isPresenter(f)?f.title:(f.name||'Your selected client video')):f.service+' story';
    copy.children[2].textContent=src?(isPresenter(f)?'Service explainer · 15 sec':(f.role||f.business||(f.local?'Not uploaded or published':'Watch with sound'))):'Client recording to be added';
    const action=card.querySelector('.mrx-card-action');action.replaceChildren(icon(src?'play':'plus'));
    card.querySelectorAll('.mrx-loop,.mrx-poster,.mrx-preview-error').forEach(v=>{if(v.tagName==='VIDEO'){v.pause();v.removeAttribute('src');v.load();videoObserver?.unobserve(v);}v.remove();});
    if(src){
      if(poster){const img=el('img','mrx-poster');img.alt='';img.src=poster;img.loading='lazy';button.append(img);}
      const v=el('video','mrx-loop');v.muted=true;v.defaultMuted=true;v.volume=0;v.autoplay=true;v.loop=true;v.playsInline=true;v.preload='none';
      v.setAttribute('muted','');v.setAttribute('playsinline','');v.setAttribute('aria-hidden','true');v.tabIndex=-1;
      v.dataset.src=safeUrl(f.previewSrc)||src;if(poster)v.poster=poster;v.style.objectPosition=f.objectPosition||'50% 35%';
      v.addEventListener('play',()=>{if(anyModal()||motion.matches||document.hidden||card.inert)v.pause();});
      v.addEventListener('error',()=>{v.dataset.failed='true';if(!card.querySelector('.mrx-preview-error'))button.append(el('span','mrx-preview-error','Preview unavailable. Open the full recording.'));});
      button.append(v);videoObserver?.observe(v);
    }
  }
  function anyModal(){return !!document.querySelector('dialog[open]');}
  function syncVideos(){
    for(const v of grid.querySelectorAll('video')){
      const card=v.closest('.mrx-card');
      const seen=bounds.get(v)===true;
      // Do not fetch preview video until visible and permitted by user settings.
      if(seen&&!motion.matches&&!saveData()&&!card.inert&&!v.getAttribute('src')&&v.dataset.failed!=='true'){v.preload='metadata';v.src=v.dataset.src;}
      const shouldPlay=!document.hidden&&!anyModal()&&!motion.matches&&!saveData()&&!card.inert&&seen&&v.dataset.failed!=='true';
      if(shouldPlay){
        if(!v.getAttribute('src'))v.src=v.dataset.src;
        if(v.paused)v.play().then(()=>{if(document.hidden||anyModal()||motion.matches||card.inert||bounds.get(v)!==true)v.pause();}).catch(()=>{});
      }else v.pause();
    }
  }
  let videoObserver=null;
  if('IntersectionObserver' in window)videoObserver=new IntersectionObserver(entries=>{entries.forEach(e=>bounds.set(e.target,e.isIntersecting));syncVideos();},{threshold:.12});
  grid.replaceChildren(); // Replace the crawlable written-review fallback, not append duplicates.
  section.classList.add('mrx-ready');
  for(const [i,f] of items.entries()){
    const card=f.kind==='written'?createWritten(f):createVideo(f,i);
    card.dataset.reviewId=f.id;card.dataset.reviewIndex=String(i);grid.append(card);cards.push(card);
  }
  function layout(){
    layoutFrame=0;const width=grid.clientWidth;if(!width)return;
    const ww=window.innerWidth;columns=ww<=600?1:ww<=800?2:ww<=1100?3:4;
    const gap=parseFloat(getComputedStyle(section).getPropertyValue('--mrx-gap'))||18;
    const cw=(width-gap*(columns-1))/columns;
    cards.forEach(c=>{c.style.width=cw+'px';});
    const heights=cards.map(c=>c.offsetHeight);const tops=Array(columns).fill(0);positions=[];
    cards.forEach((c,i)=>{
      const col=tops.indexOf(Math.min(...tops)),y=tops[col],x=col*(cw+gap);
      c.style.setProperty('--mrx-x',x+'px');c.style.setProperty('--mrx-y',y+'px');
      positions.push({x,y,height:heights[i],bottom:y+heights[i]});tops[col]=y+heights[i]+gap;
    });
    fullHeight=Math.ceil(Math.max(...tops)-gap+2);grid.style.height=fullHeight+'px';
    setHeight(false,false);
  }
  function queueLayout(){if(!layoutFrame)layoutFrame=requestAnimationFrame(layout);}
  function baseHeight(){const firstRow=Math.max(0,...positions.filter(p=>p.y===0).map(p=>p.bottom));return Math.max(columns===1?995:columns===2?775:columns===3?680:675,Math.ceil(firstRow+155));}
  function stepHeight(){return columns===1?850:columns===2?650:430;}
  function setHeight(animate,collapse){
    const target=fullyExpanded?fullHeight:Math.min(fullHeight,baseHeight()+stage*stepHeight());
    const nowFull=target>=fullHeight-2;
    const wasActive=cards.map(c=>!c.inert);
    revealHeight=target;viewport.style.height=target+'px';
    shell.classList.toggle('is-expanded',nowFull);
    section.dataset.revealStage=String(stage);section.dataset.expanded=String(nowFull);
    more.setAttribute('aria-expanded',String(nowFull));moreText.textContent=nowFull?'Show fewer':'View more';
    const activeLimit=nowFull?target:target-112;
    let activeCount=0;
    cards.forEach((c,i)=>{
      const available=positions[i].bottom<=activeLimit;
      c.inert=!available;c.setAttribute('aria-hidden',String(!available));c.dataset.visible=String(available);
      if(available){activeCount++;if(animate&&!wasActive[i]&&!motion.matches){c.classList.remove('is-revealed');requestAnimationFrame(()=>c.classList.add('is-revealed'));}}
    });
    note.textContent=nowFull?'You’ve reached the end of this collection.':activeCount+' of '+items.length+' items shown. More below.';
    more.hidden=fullHeight<=baseHeight();
    if(animate){
      more.disabled=true;viewport.setAttribute('aria-busy','true');animating=true;
      clearTimeout(finishTimer);finishTimer=setTimeout(()=>{
        animating=false;more.disabled=false;viewport.removeAttribute('aria-busy');
        live.textContent=nowFull?'All '+items.length+' items revealed.':activeCount+' of '+items.length+' items are now visible.';
        if(collapse){
          const b=more.getBoundingClientRect();
          if(b.bottom<60||b.top>window.innerHeight-80)window.scrollTo({top:window.scrollY+b.top-window.innerHeight*.68,behavior:motion.matches?'instant':'smooth'});
        }
        more.focus({preventScroll:true});syncVideos();
      },motion.matches?0:700);
    }
    syncVideos();
  }
  more.addEventListener('click',()=>{
    if(animating)return;
    const isAll=section.dataset.expanded==='true';
    if(isAll){stage=0;fullyExpanded=false;setHeight(true,true);}else{
      stage++;fullyExpanded=baseHeight()+stage*stepHeight()>=fullHeight;setHeight(true,false);
    }
  });
  if('ResizeObserver' in window){const ro=new ResizeObserver(queueLayout);ro.observe(grid);cards.forEach(c=>ro.observe(c));}
  window.addEventListener('resize',queueLayout,{passive:true});
  document.fonts?.ready.then(queueLayout);queueLayout();
  motion.addEventListener('change',()=>{queueLayout();syncVideos();});
  document.addEventListener('visibilitychange',syncVideos);
  function playbackSignal(){document.dispatchEvent(new CustomEvent('grp:client-stories-dialog-change'));}
  function resetPlayer(){player.pause();player.removeAttribute('src');player.replaceChildren();player.load();sound.hidden=true;}
  function playWithSound(){
    if(!dialog.open||!player.getAttribute('src'))return;
    player.defaultMuted=false;player.muted=false;player.volume=1;player.loop=false;player.removeAttribute('muted');
    sound.hidden=true;player.play().catch(e=>{if(e.name==='NotAllowedError'&&dialog.open)sound.hidden=false;});
  }
  sound.addEventListener('click',playWithSound);
  function fillDialog(f){
    const src=safeUrl(f.src),admin=preview&&config.allowLocalPreview===true&&!isPresenter(f);
    find('#mrx-dialog-title').textContent=src?(isPresenter(f)?f.service:(f.name||f.service+' client video')):f.service+' story';
    find('#mrx-dialog-kind').textContent=src?(isPresenter(f)?'AI-PRESENTED SERVICE EXPLAINER':(f.local?'LOCAL RECORDING PREVIEW':'CLIENT VIDEO')):'CLIENT VIDEO SPACE';
    find('#mrx-dialog-description').textContent=isPresenter(f)?f.description:src?([f.role,f.business].filter(Boolean).join(' · ')||'Use the controls for sound, captions and full-screen viewing.'):'Add the original recording with the client’s permission. AI service presenters are kept in the separate section above.';
    find('#mrx-dialog-message').textContent=isPresenter(f)?'AI-generated presenter and voice. This explains our service and is not a customer testimonial.':f.local?'Local preview. This recording has not been uploaded, published or verified.':'';
    find('#mrx-admin').hidden=!admin;
    find('#mrx-name-fields').hidden=!admin||!src;
    find('#mrx-client-name').value=f.name||'';find('#mrx-client-role').value=f.role||f.business||'';
    find('.mrx-enquire').dataset.auditService=['SEO Services','Google Ads','Local SEO','AI SEO Services'].includes(f.service)?f.service:'Not sure yet';
    find('#mrx-empty-player').hidden=!!src;player.hidden=!src;
    find('#mrx-transcript').hidden=!f.transcript;find('#mrx-transcript p').textContent=f.transcript||'';
    if(src){
      player.src=src;
      if(safeUrl(f.captions)){const t=document.createElement('track');t.kind='captions';t.srclang='en';t.label='English';t.src=safeUrl(f.captions);player.append(t);}
      playWithSound();
    }
  }
  function openVideo(index,trigger){
    const f=items[index];if(!f||f.kind!=='video')return;
    selected=index;lastTrigger=trigger||document.activeElement;
    document.querySelectorAll('dialog[open]').forEach(d=>{if(d!==dialog)d.close();});
    resetPlayer();file.value='';dialog.showModal();document.body.classList.add('modal-open');
    syncVideos();playbackSignal();fillDialog(f);
    // Pause all other ambient players immediately, including the service fan.
    document.querySelectorAll('video').forEach(v=>{if(v!==player)v.pause();});
  }
  grid.addEventListener('click',e=>{const button=e.target.closest('[data-client-film]');if(button)openVideo(Number(button.dataset.clientFilm),button);});
  dialog.addEventListener('close',()=>{
    resetPlayer();if(!anyModal())document.body.classList.remove('modal-open');
    syncVideos();playbackSignal();
    requestAnimationFrame(()=>{if(!anyModal()&&lastTrigger?.isConnected&&!lastTrigger.closest('[inert]'))lastTrigger.focus({preventScroll:true});});
  });
  player.addEventListener('error',()=>{
    if(!dialog.open||!player.getAttribute('src'))return;
    find('#mrx-dialog-message').textContent='This recording could not be played. Check its source or choose an MP4/WebM supported by this browser.';
    sound.hidden=true;
  });
  file.addEventListener('change',()=>{
    const f=file.files?.[0];if(!f||selected<0)return;
    if((!f.type.startsWith('video/')&&!/\.(mp4|webm|mov)$/i.test(f.name))||f.size>250*1024*1024){find('#mrx-dialog-message').textContent='Choose an MP4, WebM or MOV video smaller than 250 MB.';file.value='';return;}
    const url=URL.createObjectURL(f);urls.add(url);
    const data=items[selected];const previous=data.local?data.src:'';
    data.src=url;data.previewSrc=url;data.poster='';data.local=true;data.approved=false;
    data.transcript='';data.captions='';resetPlayer();updateCard(cards[selected],data,selected);fillDialog(data);queueLayout();
    if(previous&&urls.has(previous)){URL.revokeObjectURL(previous);urls.delete(previous);}
  });
  find('#mrx-apply-name').addEventListener('click',()=>{
    const f=items[selected];if(!f)return;
    f.name=find('#mrx-client-name').value.trim();f.role=find('#mrx-client-role').value.trim();
    const copy=cards[selected].querySelector('.mrx-video-copy');copy.children[1].textContent=f.name||'Your selected client video';copy.children[2].textContent=f.role||'Local preview · not published';
    find('#mrx-dialog-title').textContent=f.name||f.service+' client video';find('#mrx-dialog-description').textContent=f.role||'Original recording selected on this device.';
    find('#mrx-dialog-message').textContent='Details applied to this preview only. Nothing has been saved or uploaded.';
  });
  if('MutationObserver' in window){const mo=new MutationObserver(syncVideos);document.querySelectorAll('dialog').forEach(d=>mo.observe(d,{attributes:true,attributeFilter:['open']}));}
  window.addEventListener('pagehide',()=>{player.pause();grid.querySelectorAll('video').forEach(v=>v.pause());});
})();
;
/* SOURCE: enquiry-config.js */
/* Browser-safe configuration only. Never add API keys here.
 * Empty endpoint = design preview: no requests, storage or fake success.
 * Connect a same-origin POST endpoint returning {"success":true} after genuine receipt.
 */
window.GRP_ENQUIRY_CONFIG = Object.freeze({ endpoint: "", timeoutMs: 15000, confirmationPage: "thank-you.html" });
;
/* SOURCE: enquiry-experience.js */
/* Single-step enquiry: name, email, contact number, website, service and message.
 * Context from service / package / project buttons is carried automatically.
 * No network request or persistence unless an endpoint is explicitly configured.
 */
(() => {
  'use strict';
  const dialog = document.getElementById('audit-dialog');
  const form = document.getElementById('audit-form');
  if (!dialog || !form) return;
  const $ = selector => dialog.querySelector(selector);
  const name = form.elements.name, email = form.elements.email;
  const phone = form.elements.phone, website = form.elements.website;
  const service = form.elements.service, message = form.elements.goal;
  const feedback = $('#enquiry-result'), submit = $('#enquiry-submit');
  const title = $('#audit-title'), intro = $('#eq-intro');
  const config = window.GRP_ENQUIRY_CONFIG || {};
  const endpoint = typeof config.endpoint === 'string' ? config.endpoint.trim() : '';
  let opener = null, sending = false, controller = null;
  $('#enquiry-preview-note').hidden = Boolean(endpoint);

  function status(text, state = 'note') {
    feedback.textContent = text;
    feedback.dataset.state = state;
    feedback.hidden = !text;
  }
  function error(field, text = '') {
    const node = document.getElementById(field.id + '-error');
    if (text) field.setAttribute('aria-invalid', 'true');
    else field.removeAttribute('aria-invalid');
    if (node) { node.textContent = text; node.hidden = !text; }
  }
  function validatePhone() {
    phone.value = phone.value.trim();
    if (!phone.value) { error(phone); return true; }
    const core = phone.value.replace(/(?:ext\.?|x)\s*\d{1,6}\s*$/i, '');
    const digits = core.replace(/\D/g, '');
    if (digits.length < 7 || digits.length > 16 || /[^\d\s()+.\-]/.test(core)) {
      error(phone, 'Enter a valid contact number, or leave it blank.'); return false;
    }
    error(phone); return true;
  }
  function validateWebsite() {
    let value = website.value.trim();
    if (!value) { website.value = ''; error(website); return true; }
    if (!/^[a-z][a-z\d+.-]*:/i.test(value)) value = 'https://' + value;
    try {
      const url = new URL(value);
      if (!/^https?:$/.test(url.protocol) || url.username || url.password ||
          !url.hostname.includes('.') || /\s/.test(value)) throw new Error('Website');
      website.value = url.href; error(website); return true;
    } catch {
      error(website, 'Enter a website such as example.co.uk, or leave it blank.'); return false;
    }
  }
  function validate() {
    name.value = name.value.trim();
    email.value = email.value.trim();
    let first = null;
    if (!name.value) { error(name, 'Please enter your name.'); first = name; }
    else error(name);
    if (!email.value || !email.validity.valid) {
      error(email, 'Please enter a valid email address.');
      first ||= email;
    } else error(email);
    if (!validatePhone()) first ||= phone;
    if (!validateWebsite()) first ||= website;
    if (first) { first.focus({ preventScroll: true }); return false; }
    return true;
  }
  function syncContext() {
    const plan = form.elements.selected_plan.value;
    $('#pricing-enquiry-context').hidden = !plan;
    intro.hidden = Boolean(plan);
    if (plan) $('#pricing-enquiry-name').textContent = plan;
    // Keep the header concise, irrespective of where the visitor started.
    title.textContent = document.body.classList.contains('ai-seo-page') && service.value === 'AI SEO Services' ? 'Let’s talk about your AI visibility.' : document.body.classList.contains('google-ads-page') && service.value === 'Google Ads' ? 'Let’s talk about your Google Ads.' : (/audit/i.test(form.elements.enquiry_source.value) ? 'Request your free SEO audit.' : 'Let’s talk about your business.');
    intro.textContent = 'A few details to help us get the conversation started.';
  }
  function openEnquiry(button) {
    if (sending) return;
    opener = button instanceof HTMLElement ? button : document.activeElement;
    if (button?.dataset.auditService && [...service.options].some(o => o.value === button.dataset.auditService)) {
      service.value = button.dataset.auditService;
    }
    form.elements.enquiry_source.value = (button?.textContent || 'General enquiry').trim().replace(/\s+/g, ' ');
    if (button?.id !== 'feature-enquire') form.elements.project_context.value = button?.dataset.auditProject || '';
    document.querySelectorAll('dialog[open]').forEach(d => { if (d !== dialog) d.close(); });
    document.querySelectorAll('video').forEach(v => v.pause());
    const menu = document.querySelector('.menu-toggle'), nav = document.getElementById('primary-navigation');
    nav?.classList.remove('is-open');
    menu?.setAttribute('aria-expanded', 'false');
    menu?.setAttribute('aria-label', 'Open navigation');
    status('');
    error(name); error(email); error(phone); error(website);
    syncContext();
    form.hidden = false;
    if (!dialog.open) dialog.showModal();
    document.body.classList.add('modal-open');
    // Focus the first incomplete required field, never a hidden context input.
    requestAnimationFrame(() => {
      if (!dialog.open) return;
      (name.value ? (email.value ? message : email) : name).focus({ preventScroll: true });
      dialog.scrollTop = 0;
    });
  }
  document.addEventListener('click', event => {
    const trigger = event.target.closest('[data-audit]');
    if (!trigger) return;
    event.preventDefault();
    openEnquiry(trigger);
  });
  document.addEventListener('grp:enquiry', event => openEnquiry(event.detail?.trigger));
  $('#pricing-clear-plan')?.addEventListener('click', () => {
    form.elements.selected_plan.value = '';
    form.elements.plan_guide_rate.value = '';
    service.value = 'Not sure yet';
    syncContext();
    name.focus({ preventScroll: true });
  });
  [name, email, phone, website].forEach(field => field.addEventListener('input', () => { error(field); status(''); }));
  message.addEventListener('input', () => status(''));
  website.addEventListener('blur', () => { if (website.value.trim()) validateWebsite(); });
  service.addEventListener('change', () => { status(''); syncContext(); });

  function closeEnquiry() {
    // Abort any pending request; never imply that abort guarantees non-delivery.
    controller?.abort();
    dialog.close();
  }
  $('#enquiry-cancel').addEventListener('click', closeEnquiry);
  $('.enquiry-close').addEventListener('click', closeEnquiry);
  dialog.addEventListener('cancel', () => controller?.abort());
  // Keep keyboard navigation inside the form, including browsers that otherwise
  // pass the last Tab stop to browser chrome while a native dialog is open.
  dialog.addEventListener('keydown', event => {
    if (event.key !== 'Tab') return;
    const stops = [...dialog.querySelectorAll('button:not([disabled]), input:not([type=hidden]):not([disabled]), textarea:not([disabled]), select:not([hidden]):not([disabled]), a[href], [tabindex="0"]')]
      .filter(node => !node.hidden && node.getClientRects().length);
    const first = stops[0], last = stops[stops.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault(); last?.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault(); first?.focus();
    }
  });
  // Require a click that starts and ends on the backdrop, not a drag from a field.
  let backdropDown = false;
  const outside = event => {
    const r = dialog.getBoundingClientRect();
    return event.target === dialog &&
      (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom);
  };
  dialog.addEventListener('pointerdown', event => { backdropDown = outside(event); });
  dialog.addEventListener('click', event => { if (backdropDown && outside(event)) closeEnquiry(); backdropDown = false; });
  dialog.addEventListener('close', () => {
    controller?.abort();
    if (!document.querySelector('dialog[open]')) document.body.classList.remove('modal-open');
    // Keep unsubmitted text in memory only. Cancel never writes it to storage.
    requestAnimationFrame(() => {
      if (!document.querySelector('dialog[open]') && opener?.isConnected && !opener.closest('[inert]')) {
        opener.focus({ preventScroll: true });
      }
    });
  });

  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (sending) return;
    if(!validate()){window.GRP_METRICS?.emit('enquiry_invalid');return;}
    window.GRP_METRICS?.emit('enquiry_attempt',{service:service.value,plan:form.elements.selected_plan.value});
    if (!endpoint) {
      window.GRP_METRICS?.emit('enquiry_preview');
      status('Preview only: nothing has been sent. Your details remain in this form.');
      return;
    }
    let url;
    try {
      url = new URL(endpoint, location.href);
      if (url.origin !== location.origin || !/^https?:$/.test(url.protocol)) throw new Error();
    } catch {
      status('The enquiry connection is not configured. Please contact us using the details in the footer.', 'error');
      return;
    }
    const payload = {
      name: name.value, email: email.value, message: message.value.trim(),
      service: service.value, selectedPlan: form.elements.selected_plan.value,
      monthlyGuideRate: form.elements.plan_guide_rate.value,
      project: form.elements.project_context.value,
      source: form.elements.enquiry_source.value,
      website: form.elements.website.value, phone: form.elements.phone.value,
      page: location.pathname
    };
    sending = true; submit.disabled = true; form.setAttribute('aria-busy', 'true');
    submit.querySelector('.ui-button-label').textContent = 'Sending…';
    status('');
    controller = new AbortController();
    const timeout = setTimeout(() => controller?.abort(), Math.min(60000, Math.max(3000, Number(config.timeoutMs) || 15000)));
    try {
      const response = await fetch(url, {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload), credentials: 'same-origin', signal: controller.signal
      });
      const body = await response.json().catch(() => null);
      if (!response.ok || body?.success !== true) throw new Error('Unconfirmed receipt');
      window.GRP_METRICS?.emit('enquiry_success',{service:service.value,plan:form.elements.selected_plan.value});
      status('Thank you. Your enquiry has been received.', 'success');
      window.GRP_RECEIPT?.confirm(body,{service:service.value});
    } catch (err) {
      window.GRP_METRICS?.emit('enquiry_error');
      if (dialog.open) status(
        err.name === 'AbortError'
          ? 'We could not confirm delivery. Please check before trying again, or contact us directly.'
          : 'Your enquiry could not be confirmed. Your details are still here; please try again or contact us directly.',
        'error');
    } finally {
      clearTimeout(timeout);
      sending = false; controller = null; submit.disabled = false; form.removeAttribute('aria-busy');
      submit.querySelector('.ui-button-label').textContent = 'Send enquiry';
    }
  });
})();
;
/* SOURCE: compact-details.js */
/* Compact access to existing delivery and office information. No remote calls. */
(() => {
 'use strict';
 const rows = [{"key": "scope", "title": "Clear scope", "question": "What work is actually included?", "lead": "A defined plan from the start.", "answer": "Agree the deliverables, priorities and responsibilities before any work begins.", "icon": "#fa-list-check"}, {"key": "channels", "title": "Right service mix", "question": "Which channels does my business need?", "lead": "Your goals set the direction.", "answer": "Choose the right services for your audience, priorities and budget. Each channel should have a clear purpose.", "icon": "#fa-magnifying-glass-chart"}, {"key": "access", "title": "Account ownership", "question": "Who controls my website and advertising accounts?", "lead": "Your assets. Clear access.", "answer": "Clarify account ownership, permissions and responsibilities from the outset.", "icon": "#fa-key"}, {"key": "reporting", "title": "Useful reporting", "question": "How will I understand what is happening?", "lead": "Progress you can follow.", "answer": "See the work completed, the relevant performance data and the recommended next steps.", "icon": "#fa-chart-column"}, {"key": "contact", "title": "Ongoing communication", "question": "Who do I speak to, and when?", "lead": "A clear point of contact.", "answer": "Agree who leads your project, how updates are shared and when priorities are reviewed.", "icon": "#fa-comments"}];
 const outlines = {
    scope: {
      title: 'An agreed scope of work',
      subtitle: 'Scope outline',
      intro: 'A shared starting point: what is included, why it matters and who is responsible. Your own scope is agreed around your business.',
      items: [
        ['Your starting point', 'Business goals, existing channels and the issues the project needs to address.'],
        ['Deliverables and priorities', 'The work included, the order of priorities and the dependencies involved.'],
        ['Responsibilities', 'Who provides access, prepares content, reviews the work and gives approval.'],
        ['Boundaries and changes', 'What sits outside the agreed scope and how extra work is discussed before it starts.']
      ]
    },
    channels: {
      title: 'A channel plan with a purpose',
      subtitle: 'Channel-plan outline',
      intro: 'The right starting point is your audience and business goal, not a list of channels. This outline shows the decisions a plan should make clear.',
      items: [
        ['Audience and demand', 'Who you need to reach, where they search and the questions they need answered.'],
        ['Channel priorities', 'Which services are appropriate now, which can wait and the reason for each choice.'],
        ['The customer journey', 'The pages, messages and next actions that connect visibility to an enquiry or sale.'],
        ['Measurement and budget', 'The measures to monitor and a clear distinction between agency fees and advertising spend.']
      ]
    },
    access: {
      title: 'Account access, clearly agreed',
      subtitle: 'Access outline',
      intro: 'Know which assets are involved and how access is managed. Permissions and ownership should be clear before the team starts work.',
      items: [
        ['Asset register', 'The relevant website, domain, advertising, business profile and analytics accounts.'],
        ['Ownership and permissions', 'The account owner, the access needed for the work and who authorises it.'],
        ['Working access', 'Use named invitations and appropriate permissions rather than sharing personal passwords.'],
        ['Changes and handover', 'How access changes, approvals and handover are recorded and agreed.']
      ]
    },
    reporting: {
      title: 'Reporting that explains the work',
      subtitle: 'Progress-report outline',
      intro: 'A useful report connects activity with the available evidence. It should help you understand what happened and what is recommended next.',
      items: [
        ['Work completed', 'A clear summary of the changes and deliverables completed during the agreed period.'],
        ['Relevant measures', 'The agreed performance measures, their source and the reporting dates.'],
        ['Context and limitations', 'What the figures mean, relevant changes and any gaps or limits in the available tracking.'],
        ['Next actions', 'Recommended priorities, decisions required and the work proposed for the next period.']
      ]
    },
    contact: {
      title: 'A clear communication plan',
      subtitle: 'Contact-plan outline',
      intro: 'Good communication starts with knowing who to contact and how decisions are made. These details are agreed for the project, not assumed.',
      items: [
        ['Your point of contact', 'The person coordinating the project and the people responsible for approvals.'],
        ['Update arrangements', 'The channels and frequency for progress updates, agreed around the work.'],
        ['Questions and decisions', 'Where questions, feedback and outstanding decisions are recorded.'],
        ['Review points', 'When priorities, scope and the next steps are reviewed together.']
      ]
    }
  };
 const offices = [{"city": "London", "address": "Tower 42, 25 Old Broad St, London EC2N 1HN", "phone": "020 8865 1917", "href": "tel:+442088651917"}, {"city": "Birmingham", "address": "Lewis Building, 35 Bull St, Birmingham B4 6AF", "phone": "0121 339 5365", "href": "tel:+441213395365"}, {"city": "Slough", "address": "9 Mackenzie St, Slough SL1 1XQ", "phone": "01753 318 308", "href": "tel:+441753318308"}, {"city": "Manchester", "address": "Peter House, Oxford St, Manchester M1 5AN", "phone": "0161 726 5295", "href": "tel:+441617265295"}];
 const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text)n.textContent=text;return n;};
 const icon=(id)=>{const n=document.createElementNS('http://www.w3.org/2000/svg','svg');n.setAttribute('class','grp-icon fa-icon');n.setAttribute('aria-hidden','true');const u=document.createElementNS(n.namespaceURI,'use');u.setAttribute('href',id);n.append(u);return n;};
 const open=(title,content,trigger)=>document.dispatchEvent(new CustomEvent('grp:information',{detail:{title,content,trigger}}));
 document.querySelectorAll('[data-working-approach]').forEach(trigger=>trigger.addEventListener('click',()=>{
  const content=el('div','compact-approach');
  content.append(el('p','compact-dialog-intro','Know the plan. See the work. Five essentials to agree before your project begins.'));
  const group=el('div','compact-approach-list');
  rows.forEach((row,index)=>{
   const detail=el('details','compact-approach-item');
   const summary=el('summary');
   const label=el('span','compact-approach-label');label.append(el('strong','',row.title),el('small','',row.lead));
   const mark=el('span','compact-dialog-icon');mark.append(icon(row.icon));
   summary.append(mark,label,icon('#fa-angle-right'));detail.append(summary);
   const body=el('div','compact-approach-body');body.append(el('p','compact-question',row.question),el('p','',row.answer));
   const record=outlines[row.key];
   body.append(el('h3','',record.subtitle),el('p','',record.intro));
   const list=el('ol','compact-outline-list');
   record.items.forEach(([title,description])=>{const li=el('li');li.append(el('strong','',title),el('span','',description));list.append(li);});
   body.append(list);detail.append(body);group.append(detail);
  });
  content.append(group,el('p','compact-dialog-note','Illustrative outlines, not final proposals. Your proposal confirms the deliverables, costs, access arrangements and update schedule; these examples do not add commitments to an existing agreement.'));
  open('How we work',content,trigger);
 }));
 document.querySelectorAll('[data-footer-locations]').forEach(trigger=>trigger.addEventListener('click',()=>{
  const content=el('div','compact-office-details');
  content.append(el('p','compact-dialog-intro','All four office addresses and telephone numbers, together in one place.'));
  const grid=el('div','compact-offices-grid');
  offices.forEach(office=>{
   const card=el('div','compact-office-card');const label=el('div','compact-office-heading');label.append(icon('#fa-map-location-dot'),el('h3','',office.city));
   const address=el('address','',office.address);const phone=el('a','compact-office-phone',office.phone);phone.href=office.href;phone.append(icon('#fa-angle-right'));
   card.append(label,address,phone);grid.append(card);
  });
  content.append(grid,el('p','compact-office-hours','Telephone hours: Mon–Sat, 09:30–18:00 · UK time.'));
  open('Our UK locations',content,trigger);
 }));
 const small=matchMedia('(max-width:700px)');
 const menus=[...document.querySelectorAll('[data-compact-nav]')];
 const syncMenus=()=>menus.forEach(d=>{d.open=!small.matches;});
 syncMenus();small.addEventListener('change',syncMenus);
 menus.forEach(d=>d.querySelector('summary').addEventListener('click',event=>{if(!small.matches)event.preventDefault();}));
 // Preserve old shared links without keeping a large empty section on the page.
 if(location.hash==='#our-difference'){
  const t=document.querySelector('[data-working-approach]');
  if(t)requestAnimationFrame(()=>{t.scrollIntoView({block:'center'});t.click();});
 }
})();
;
/* SOURCE: contact-navigation.js */
/* Contact navigation only. No personal information is written to URLs or storage. */
(()=>{'use strict';
 const page=document.body.dataset.pageId||'';
 const services={'seo-services':'SEO Services','local-seo':'Local SEO','google-ads':'Google Ads','ai-seo':'AI SEO Services'};
 function update(){
  document.querySelectorAll('[data-contact-page]').forEach(link=>{
   const params=new URLSearchParams();
   const service=services[page];if(service)params.set('service',service);
   const plan=document.querySelector('[data-detail-plan][aria-selected="true"]')?.dataset.detailPlan
    ||document.querySelector('[data-plan-focus][aria-pressed="true"]')?.dataset.planFocus;
   if(['local','growth','authority'].includes(plan))params.set('plan',plan);
   link.setAttribute('href','contact-us.html'+(params.size?'?'+params.toString():''));
  });
 }
 // Refresh on activation so a newly selected pricing plan carries through.
 document.addEventListener('click',e=>{if(e.target.closest('[data-contact-page]'))update();},true);
 document.addEventListener('auxclick',e=>{if(e.target.closest('[data-contact-page]'))update();},true);
 update();
})();
;
/* SOURCE: privacy-controls.js */
/* No automatic cookie banner when no optional integration is installed.
   Preference storage is written on Save / Reject / Accept only, never on browsing. */
(()=>{'use strict';
 const KEY='grp.cookie-choice.v1',cfg=window.GRP_PRIVACY_CONFIG||{},version=cfg.version||'v1';
 const scripts=Array.isArray(cfg.scripts)?cfg.scripts:[];const optional=scripts.filter(s=>['analytics','marketing'].includes(s.category)&&s.id&&s.src);
 const installed=category=>optional.some(s=>s.category===category);
 const currentEmpty=()=>({version,analytics:false,marketing:false,expires:0});let choice=currentEmpty(),persistent=true,modal=null,opener=null;const loaded=new Set();
 function read(){try{const v=JSON.parse(localStorage.getItem(KEY)||'null');if(v?.version===version&&Number(v.expires)>Date.now()){choice={version,analytics:v.analytics===true,marketing:v.marketing===true,expires:Number(v.expires)};}else if(v){localStorage.removeItem(KEY);}}catch{persistent=false;}return choice;}
 function status(){const n=document.getElementById('sp-cookie-status');if(!n)return;n.textContent=choice.expires?'Preference saved. Optional analytics '+(choice.analytics?'allowed':'off')+'; advertising '+(choice.marketing?'allowed':'off')+'.':'No saved choice. No optional scripts are enabled.';}
 function load(){for(const p of optional){if(!choice[p.category]||loaded.has(p.id))continue;let url;try{url=new URL(p.src,location.href);if(url.protocol!=='https:'&&!(url.origin===location.origin&&url.protocol==='http:'))continue;}catch{continue;}const s=document.createElement('script');s.src=url.href;s.async=true;s.dataset.grpOptional=String(p.id);loaded.add(p.id);document.head.append(s);}}
 function revoke(old,next){let any=false;for(const p of optional){if(!old[p.category]||next[p.category])continue;if(loaded.has(p.id))any=true;for(const key of Array.isArray(p.cookies)?p.cookies:[]){if(!/^[A-Za-z0-9_.-]+$/.test(key))continue;document.cookie=key+'=; Max-Age=0; Path=/; SameSite=Lax';}}
 return any;}
 function write(next){const old=choice;choice={version,analytics:installed('analytics')&&next.analytics===true,marketing:installed('marketing')&&next.marketing===true,expires:Date.now()+Math.min(365,Math.max(1,Number(cfg.retentionDays)||180))*864e5};
 try{localStorage.setItem(KEY,JSON.stringify(choice));persistent=true;}catch{persistent=false;}
 const reload=revoke(old,choice);status();load();document.dispatchEvent(new CustomEvent('grp:privacy-change',{detail:{analytics:choice.analytics,marketing:choice.marketing}}));
 const live=modal?.querySelector('[data-cookie-feedback]');if(live)live.textContent=persistent?'Your preferences have been saved.':'Choice applied for this page. Your browser did not allow us to save it.';
 if(reload){setTimeout(()=>location.reload(),80);}return persistent;}
 function close(){modal?.close();if(!document.querySelector('dialog[open]'))document.body.classList.remove('modal-open');opener?.focus?.({preventScroll:true});}
 function open(trigger){opener=trigger||document.activeElement;
 if(!modal){modal=document.createElement('dialog');modal.className='privacy-dialog';modal.id='privacy-settings-dialog';modal.setAttribute('aria-labelledby','privacy-settings-title');modal.innerHTML=`<div class="pc-header"><div><p>YOUR PRIVACY CHOICES</p><h2 id="privacy-settings-title">Cookie settings<span>.</span></h2></div><button type="button" data-pc-close aria-label="Close cookie settings">×</button></div><p class="pc-intro">Keep control of optional tools. Your main website experience stays available when you reject them.</p><div class="pc-row"><div><h3>Necessary storage</h3><p>Remembers your choice and shows a confirmed enquiry status. No contact details are stored.</p></div><span class="pc-locked">Always active</span></div>${['analytics','marketing'].map(c=>`<div class="pc-row"><div><h3>${c==='analytics'?'Analytics':'Advertising'}</h3><p>${installed(c)?'Only the configured, approved '+(c==='analytics'?'measurement':'advertising')+' scripts.':'Not installed in this review build.'}</p></div><label class="pc-toggle"><input type="checkbox" name="${c}" aria-label="Allow ${c}" ${installed(c)?'':'disabled'}><span></span></label></div>`).join('')}<p class="pc-resource-note">Font and direct video-file requests are separate delivery resources. <a href="cookie-policy.html#providers">Read the resource information</a>.</p><div class="pc-actions"><button type="button" data-pc-reject>Reject optional</button>${optional.length?'<button type="button" data-pc-accept>Accept optional</button>':''}<button type="button" data-pc-save class="pc-save">Save choices</button></div><div class="pc-bottom"><button type="button" data-pc-reset>Reset saved choices</button><a href="cookie-policy.html">Cookie information</a></div><p class="pc-feedback" data-cookie-feedback role="status" aria-live="polite"></p>`;document.body.append(modal);
 modal.querySelector('[data-pc-close]').addEventListener('click',close);
 modal.querySelector('[data-pc-save]').addEventListener('click',()=>write({analytics:modal.querySelector('[name=analytics]').checked,marketing:modal.querySelector('[name=marketing]').checked}));
 modal.querySelector('[data-pc-reject]').addEventListener('click',()=>{modal.querySelectorAll('input[type=checkbox]').forEach(x=>x.checked=false);write({});});
 modal.querySelector('[data-pc-accept]')?.addEventListener('click',()=>{modal.querySelectorAll('input[type=checkbox]:not([disabled])').forEach(x=>x.checked=true);write({analytics:true,marketing:true});});
 modal.querySelector('[data-pc-reset]').addEventListener('click',()=>{const reload=revoke(choice,{});try{localStorage.removeItem(KEY);}catch{}choice=currentEmpty();modal.querySelectorAll('input[type=checkbox]').forEach(x=>x.checked=false);status();modal.querySelector('[data-cookie-feedback]').textContent='Saved choices removed. Optional tools stay off.';if(reload)location.reload();});
 modal.addEventListener('close',()=>{if(!document.querySelector('dialog[open]'))document.body.classList.remove('modal-open');opener?.focus?.({preventScroll:true});});
 modal.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const items=[...modal.querySelectorAll('button:not([disabled]),a[href],input:not([disabled])')].filter(x=>x.getClientRects().length);let a=items[0],b=items.at(-1);if(e.shiftKey&&document.activeElement===a){e.preventDefault();b.focus();}else if(!e.shiftKey&&document.activeElement===b){e.preventDefault();a.focus();}});
 }
 modal.querySelector('[name=analytics]').checked=choice.analytics;modal.querySelector('[name=marketing]').checked=choice.marketing;modal.querySelector('[data-cookie-feedback]').textContent='';
 document.querySelectorAll('dialog[open]').forEach(d=>{if(d!==modal)d.close();});document.querySelectorAll('video').forEach(v=>v.pause());if(!modal.open)modal.showModal();document.body.classList.add('modal-open');}
 document.addEventListener('click',e=>{const t=e.target.closest('[data-cookie-settings]');if(!t)return;e.preventDefault();open(t);});
 read();status();load();if(optional.length&&!choice.expires)open(null);
 window.GRP_PRIVACY=Object.freeze({open,read:()=>({...choice}),hasOptional:optional.length>0});
})();
;
/* SOURCE: receipt.js */
/* A navigation destination, not a receipt server. Never infer success from a URL.
   The existing form controllers call confirm only AFTER response.ok && success===true.
   No contact details, form text or email address are put into URLs or browser storage. */
(()=>{'use strict';
 const KEY='grp.enquiry.receipt.v1',TTL=30*60*1000;
 const allowed=new Set(['Not sure yet','SEO Services','AI SEO Services','Local SEO','Google Ads']);
 function go(href){const event=new CustomEvent('grp:navigate',{detail:{href},cancelable:true});if(document.dispatchEvent(event))location.assign(href);}
 function confirm(ack,context={}){
  if(!ack||ack.success!==true)return false;
  const entry={created:Date.now(),expires:Date.now()+TTL,service:allowed.has(context.service)?context.service:'Not sure yet',reference:typeof ack.reference==='string'?ack.reference.replace(/[^A-Za-z0-9_\-]/g,'').slice(0,60):''};
  try{sessionStorage.setItem(KEY,JSON.stringify(entry));}catch{return false;}
  const config=window.GRP_ENQUIRY_CONFIG||{};
  if(config.confirmationPage==='thank-you.html')go('thank-you.html');
  return true;
 }
 window.GRP_RECEIPT=Object.freeze({confirm});
 if(document.body.dataset.pageId!=='thank-you')return;
 let entry=null;try{entry=JSON.parse(sessionStorage.getItem(KEY)||'null');}catch{}
 const valid=entry&&Number(entry.created)<=Date.now()&&Number(entry.expires)>Date.now()&&Number(entry.expires)-Number(entry.created)<=TTL;
 if(!valid){try{sessionStorage.removeItem(KEY);}catch{}return;}
 const h=document.getElementById('sp-receipt-heading');h.innerHTML='Thank you.<br><span>We have your enquiry<i>.</i></span>';
 document.getElementById('sp-receipt-kicker').textContent='ENQUIRY ACKNOWLEDGED';
 document.getElementById('sp-receipt-description').textContent='The enquiry service confirmed receipt. Our team will review the information you supplied and contact you using the details in your request.';
 document.getElementById('sp-receipt-steps').hidden=false;
 const meta=document.getElementById('sp-receipt-meta');meta.hidden=false;meta.textContent=(allowed.has(entry.service)&&entry.service!=='Not sure yet'?entry.service+' · ':'')+'Received '+new Date(entry.created).toLocaleString('en-GB')+(entry.reference?' · Reference '+entry.reference:'');
 // No conversion event here: successful submission was recorded at the source form.
})();
;
/* SOURCE: support-pages.js */
/* Small progressive enhancements; all guide and policy text exists in HTML. */
(()=>{'use strict';
 const reduced=matchMedia('(prefers-reduced-motion:reduce)');
 document.querySelectorAll('[data-work-filter]').forEach(b=>b.addEventListener('click',()=>{
  const selected=b.dataset.workFilter;let count=0;
  document.querySelectorAll('[data-work-filter]').forEach(n=>n.setAttribute('aria-pressed',String(n===b)));
  document.querySelectorAll('[data-work-category]').forEach(card=>{const show=selected==='all'||card.dataset.workCategory===selected;card.hidden=!show;if(show){count++;if(!reduced.matches)card.animate([{opacity:.5,transform:'translateY(6px)'},{opacity:1,transform:'translateY(0)'}],{duration:210,easing:'ease-out'});}});
  const status=document.getElementById('sp-work-status');if(status)status.textContent=count+' example'+(count!==1?'s':'')+' shown.';
 }));
 const image=document.getElementById('sp-project-image');
 document.querySelectorAll('[data-project-view]').forEach(b=>b.addEventListener('click',()=>{
  if(!image)return;const before=b.dataset.projectView==='before';image.src=before?image.dataset.before:image.dataset.after;image.alt=before?'Earlier Google Ranker Pro homepage concept':'Current Google Ranker Pro homepage design';
  document.querySelectorAll('[data-project-view]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
  document.getElementById('sp-project-caption').textContent=(before?'Earlier concept':'Current design')+' · Actual project screenshot. Not an analytics report.';
  if(!reduced.matches)image.animate([{opacity:.6},{opacity:1}],{duration:220});
 }));
 const details=document.querySelector('.sp-reading-nav details');if(details){const m=matchMedia('(max-width:800px)');const update=()=>details.open=!m.matches;update();m.addEventListener('change',update);}
 if('IntersectionObserver'in window){const nav=document.querySelector('.sp-reading-nav nav');if(nav){const observe=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){nav.querySelectorAll('a').forEach(a=>{if(a.hash==='#'+e.target.id)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});}},{rootMargin:'-8% 0px -65% 0px'});document.querySelectorAll('.sp-reading-section').forEach(s=>observe.observe(s));}}
 // Reporting samples link into the existing homepage comparison, not fake client pages.
 const q=new URLSearchParams(location.search).get('comparison');
 if(q){const map={seo:'seo',local:'local',ads:'ads'};if(map[q]){setTimeout(()=>{const index=(window.GRP_PROOF_CONTENT?.comparisons||[]).findIndex(x=>x.id===map[q]);if(index>=0)document.querySelector(`[data-proof-index="${index}"]`)?.click();},50);}}
})();
;
/* SOURCE: social-follow.js */
/* Design-preview feedback only. Approved HTTPS profile links are baked into HTML
 * by tools/social_components.py. No third-party social widgets or trackers. */
(() => {
 'use strict';
 let timer, message;
 const dismiss=()=>{if(message)message.hidden=true;clearTimeout(timer);};
 document.addEventListener('click',event=>{
  const button=event.target.closest('button[data-social-pending]');
  if(!button){dismiss();return;}
  if(!message){message=document.createElement('div');message.className='grp-follow-status';message.id='grp-follow-status';message.setAttribute('role','status');message.setAttribute('aria-live','polite');message.setAttribute('aria-atomic','true');document.body.append(message);}
  clearTimeout(timer);
  message.textContent=button.dataset.socialPending+' profile link has not been connected in this design preview.';
  message.hidden=false;
  timer=setTimeout(dismiss,6500);
 });
 document.addEventListener('keydown',event=>{if(event.key==='Escape')dismiss();});
 window.addEventListener('pagehide',dismiss);
})();
