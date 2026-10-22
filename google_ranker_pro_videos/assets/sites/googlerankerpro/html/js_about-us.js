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
/* SOURCE: seo-team-content.js */
/* Design data only: no verified names, qualifications or staff headcount. */
window.GRP_SEO_TEAM = {
  "groups": [
    {
      "id": "strategy",
      "label": "SEO strategy",
      "description": "Search direction, campaign planning and client coordination."
    },
    {
      "id": "technical",
      "label": "Technical SEO",
      "description": "Website access, performance, migrations and technical quality."
    },
    {
      "id": "content",
      "label": "Content & on-page",
      "description": "Research, useful service content and page-level optimisation."
    },
    {
      "id": "local",
      "label": "Local & e-commerce",
      "description": "Local discovery, location pages and online product visibility."
    },
    {
      "id": "authority",
      "label": "Authority & outreach",
      "description": "Relevant outreach, digital PR and off-page SEO."
    },
    {
      "id": "ai",
      "label": "AI & analytics",
      "description": "Clear information for AI-assisted search and meaningful SEO measurement."
    }
  ],
  "profiles": [
    {
      "id": "seo-profile-01",
      "index": 1,
      "name": "",
      "role": "Head of SEO",
      "group": "strategy",
      "specialism": "SEO strategy",
      "summary": "Sets the direction for a connected SEO programme.",
      "responsibilities": [
        "Define priorities around business goals",
        "Coordinate SEO disciplines and quality standards",
        "Review the roadmap and available evidence"
      ],
      "image": "assets/about/seo-team/profile-01.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-02",
      "index": 2,
      "name": "",
      "role": "SEO Strategy Lead",
      "group": "strategy",
      "specialism": "SEO strategy",
      "summary": "Turns business priorities into a practical search roadmap.",
      "responsibilities": [
        "Plan search opportunities and page priorities",
        "Connect technical, content and authority work",
        "Agree a sequence for implementation"
      ],
      "image": "assets/about/seo-team/profile-02.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-03",
      "index": 3,
      "name": "",
      "role": "Senior SEO Consultant",
      "group": "strategy",
      "specialism": "SEO strategy",
      "summary": "Investigates complex search issues and opportunities.",
      "responsibilities": [
        "Review the website and competitive landscape",
        "Explain recommended changes and trade-offs",
        "Guide strategic decisions with available data"
      ],
      "image": "assets/about/seo-team/profile-03.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-04",
      "index": 4,
      "name": "",
      "role": "SEO Campaign Manager",
      "group": "strategy",
      "specialism": "SEO strategy",
      "summary": "Keeps the agreed SEO work moving forward.",
      "responsibilities": [
        "Coordinate deliverables and dependencies",
        "Track campaign actions and approvals",
        "Review priorities with the specialist team"
      ],
      "image": "assets/about/seo-team/profile-04.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-05",
      "index": 5,
      "name": "",
      "role": "SEO Account Manager",
      "group": "strategy",
      "specialism": "SEO strategy",
      "summary": "Connects the SEO programme with the client’s goals.",
      "responsibilities": [
        "Keep the scope and expectations clear",
        "Coordinate feedback and decisions",
        "Explain progress and next priorities"
      ],
      "image": "assets/about/seo-team/profile-05.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-06",
      "index": 6,
      "name": "",
      "role": "Technical SEO Lead",
      "group": "technical",
      "specialism": "Technical SEO",
      "summary": "Sets technical priorities across the website.",
      "responsibilities": [
        "Review crawlability and indexability",
        "Prioritise technical fixes with developers",
        "Validate important releases"
      ],
      "image": "assets/about/seo-team/profile-06.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-07",
      "index": 7,
      "name": "",
      "role": "Technical SEO Specialist",
      "group": "technical",
      "specialism": "Technical SEO",
      "summary": "Improves the foundations search engines rely on.",
      "responsibilities": [
        "Review redirects, canonical URLs and site structure",
        "Investigate crawl and indexing issues",
        "Check implementation and structured data"
      ],
      "image": "assets/about/seo-team/profile-07.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-08",
      "index": 8,
      "name": "",
      "role": "SEO Audit Specialist",
      "group": "technical",
      "specialism": "Technical SEO",
      "summary": "Finds and prioritises issues worth addressing.",
      "responsibilities": [
        "Review technical and on-page signals",
        "Separate critical issues from lower-impact tasks",
        "Document a practical action plan"
      ],
      "image": "assets/about/seo-team/profile-08.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-09",
      "index": 9,
      "name": "",
      "role": "SEO Migration Specialist",
      "group": "technical",
      "specialism": "Technical SEO",
      "summary": "Plans changes when sites, URLs or platforms move.",
      "responsibilities": [
        "Map old and new URLs",
        "Prepare redirects and migration checks",
        "Monitor visibility and indexing after release"
      ],
      "image": "assets/about/seo-team/profile-09.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-10",
      "index": 10,
      "name": "",
      "role": "International SEO Specialist",
      "group": "technical",
      "specialism": "Technical SEO",
      "summary": "Helps organise search across countries and languages.",
      "responsibilities": [
        "Review international site architecture",
        "Check language and regional targeting",
        "Coordinate localised content requirements"
      ],
      "image": "assets/about/seo-team/profile-10.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-11",
      "index": 11,
      "name": "",
      "role": "SEO Content Strategist",
      "group": "content",
      "specialism": "Content & on-page",
      "summary": "Builds a content plan around useful customer questions.",
      "responsibilities": [
        "Map topics to search intent",
        "Prioritise service pages and supporting content",
        "Plan updates around evidence and relevance"
      ],
      "image": "assets/about/seo-team/profile-11.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-12",
      "index": 12,
      "name": "",
      "role": "SEO Copywriter",
      "group": "content",
      "specialism": "Content & on-page",
      "summary": "Writes useful content for people searching for a solution.",
      "responsibilities": [
        "Draft clear service and supporting pages",
        "Answer relevant customer questions",
        "Connect useful explanations with the next step"
      ],
      "image": "assets/about/seo-team/profile-12.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-13",
      "index": 13,
      "name": "",
      "role": "On-Page SEO Specialist",
      "group": "content",
      "specialism": "Content & on-page",
      "summary": "Makes individual pages clearer and better connected.",
      "responsibilities": [
        "Review titles, headings and internal links",
        "Improve page focus and content structure",
        "Check how each page supports its search intent"
      ],
      "image": "assets/about/seo-team/profile-13.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-14",
      "index": 14,
      "name": "",
      "role": "Keyword Research Specialist",
      "group": "content",
      "specialism": "Content & on-page",
      "summary": "Finds the language and questions customers use.",
      "responsibilities": [
        "Research intent and relevant query groups",
        "Map demand to appropriate pages",
        "Review gaps and competing search results"
      ],
      "image": "assets/about/seo-team/profile-14.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-15",
      "index": 15,
      "name": "",
      "role": "SEO Content Editor",
      "group": "content",
      "specialism": "Content & on-page",
      "summary": "Keeps search content accurate, clear and consistent.",
      "responsibilities": [
        "Review clarity and factual support",
        "Maintain tone, formatting and useful structure",
        "Identify outdated or duplicated content"
      ],
      "image": "assets/about/seo-team/profile-15.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-16",
      "index": 16,
      "name": "",
      "role": "Local SEO Manager",
      "group": "local",
      "specialism": "Local & e-commerce",
      "summary": "Plans local visibility around the areas a business serves.",
      "responsibilities": [
        "Review the local search landscape",
        "Plan location and service-area content",
        "Coordinate business-profile and website work"
      ],
      "image": "assets/about/seo-team/profile-16.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-17",
      "index": 17,
      "name": "",
      "role": "Business Profile SEO Specialist",
      "group": "local",
      "specialism": "Local & e-commerce",
      "summary": "Keeps local business-profile information useful and accurate.",
      "responsibilities": [
        "Review categories and business information",
        "Coordinate relevant photographs and updates",
        "Check consistency with the business website"
      ],
      "image": "assets/about/seo-team/profile-17.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-18",
      "index": 18,
      "name": "",
      "role": "Local SEO Specialist",
      "group": "local",
      "specialism": "Local & e-commerce",
      "summary": "Connects local information with relevant website pages.",
      "responsibilities": [
        "Review location and service-area pages",
        "Check local business-information consistency",
        "Identify local search opportunities"
      ],
      "image": "assets/about/seo-team/profile-18.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-19",
      "index": 19,
      "name": "",
      "role": "Multi-Location SEO Specialist",
      "group": "local",
      "specialism": "Local & e-commerce",
      "summary": "Coordinates consistent search work across several locations.",
      "responsibilities": [
        "Plan a useful location-page structure",
        "Review each location’s business information",
        "Organise location-level reporting"
      ],
      "image": "assets/about/seo-team/profile-19.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-20",
      "index": 20,
      "name": "",
      "role": "E-commerce SEO Specialist",
      "group": "local",
      "specialism": "Local & e-commerce",
      "summary": "Improves how shoppers discover product and category pages.",
      "responsibilities": [
        "Review category structure and product content",
        "Check facets, canonicals and internal links",
        "Prioritise relevant shopping-search opportunities"
      ],
      "image": "assets/about/seo-team/profile-20.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-21",
      "index": 21,
      "name": "",
      "role": "SEO Outreach Manager",
      "group": "authority",
      "specialism": "Authority & outreach",
      "summary": "Plans relevant outreach to support organic visibility.",
      "responsibilities": [
        "Research relevant publishers and organisations",
        "Coordinate outreach and follow-ups",
        "Review relevance and quality before placement"
      ],
      "image": "assets/about/seo-team/profile-21.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-22",
      "index": 22,
      "name": "",
      "role": "SEO Digital PR Specialist",
      "group": "authority",
      "specialism": "Authority & outreach",
      "summary": "Connects useful expertise and stories with relevant publications.",
      "responsibilities": [
        "Identify evidence-led story opportunities",
        "Prepare useful expert contributions",
        "Track relevant coverage and citations"
      ],
      "image": "assets/about/seo-team/profile-22.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-23",
      "index": 23,
      "name": "",
      "role": "SEO Link Outreach Specialist",
      "group": "authority",
      "specialism": "Authority & outreach",
      "summary": "Builds relationships around relevant, useful content.",
      "responsibilities": [
        "Research contextual link opportunities",
        "Prepare personalised outreach",
        "Review placement relevance and quality"
      ],
      "image": "assets/about/seo-team/profile-23.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-24",
      "index": 24,
      "name": "",
      "role": "Off-Page SEO Specialist",
      "group": "authority",
      "specialism": "Authority & outreach",
      "summary": "Reviews the signals around a business beyond its website.",
      "responsibilities": [
        "Assess relevant links and mentions",
        "Review off-page opportunities and risks",
        "Coordinate credible authority-building work"
      ],
      "image": "assets/about/seo-team/profile-24.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-25",
      "index": 25,
      "name": "",
      "role": "SEO Outreach Coordinator",
      "group": "authority",
      "specialism": "Authority & outreach",
      "summary": "Keeps outreach research and communication organised.",
      "responsibilities": [
        "Maintain publisher and opportunity records",
        "Coordinate responses and follow-ups",
        "Document approved outreach activity"
      ],
      "image": "assets/about/seo-team/profile-25.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-26",
      "index": 26,
      "name": "",
      "role": "AI SEO Strategist",
      "group": "ai",
      "specialism": "AI & analytics",
      "summary": "Connects search foundations with AI-assisted discovery.",
      "responsibilities": [
        "Research customer questions and information gaps",
        "Improve useful, evidence-led service explanations",
        "Set realistic measurement and review priorities"
      ],
      "image": "assets/about/seo-team/profile-26.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-27",
      "index": 27,
      "name": "",
      "role": "Answer Engine SEO Specialist",
      "group": "ai",
      "specialism": "AI & analytics",
      "summary": "Organises clear answers to relevant customer questions.",
      "responsibilities": [
        "Structure direct and contextual answers",
        "Identify appropriate supporting evidence",
        "Review technical access and content clarity"
      ],
      "image": "assets/about/seo-team/profile-27.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-28",
      "index": 28,
      "name": "",
      "role": "Semantic SEO Specialist",
      "group": "ai",
      "specialism": "AI & analytics",
      "summary": "Improves the relationships between topics and business information.",
      "responsibilities": [
        "Map related topics and entities",
        "Review content coverage and internal connections",
        "Align structured information with visible content"
      ],
      "image": "assets/about/seo-team/profile-28.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-29",
      "index": 29,
      "name": "",
      "role": "SEO Data Analyst",
      "group": "ai",
      "specialism": "AI & analytics",
      "summary": "Turns available search data into useful decisions.",
      "responsibilities": [
        "Review organic traffic and enquiry measures",
        "Compare appropriate reporting periods",
        "Explain trends, limitations and opportunities"
      ],
      "image": "assets/about/seo-team/profile-29.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    },
    {
      "id": "seo-profile-30",
      "index": 30,
      "name": "",
      "role": "SEO Reporting Specialist",
      "group": "ai",
      "specialism": "AI & analytics",
      "summary": "Makes the work and its available evidence easy to understand.",
      "responsibilities": [
        "Summarise completed SEO activity",
        "Present agreed metrics with context",
        "Document recommended next steps"
      ],
      "image": "assets/about/seo-team/profile-30.webp",
      "imageWidth": 225,
      "imageHeight": 225,
      "sample": true,
      "approved": false
    }
  ]
};
;
/* SOURCE: about-us.js */
/* About page. All SEO profiles are explicitly labelled design samples. */
(() => {
 'use strict';
 const root=document.querySelector('.ab-main');if(!root)return;
 const team=root.querySelector('#our-team');
 const config=window.GRP_SEO_TEAM;
 const profiles=new Map((config?.profiles||[]).map(p=>[p.id,p]));
 const icon=id=>{const s=document.createElementNS('http://www.w3.org/2000/svg','svg');s.setAttribute('class','grp-icon fa-icon');s.setAttribute('aria-hidden','true');const u=document.createElementNS(s.namespaceURI,'use');u.setAttribute('href','#fa-'+id);s.append(u);return s;};
 const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text)n.textContent=text;return n;};
 if(team&&profiles.size){
  const cards=[...team.querySelectorAll('[data-team-id]')];
  const filters=[...team.querySelectorAll('[data-team-filter]')];
  const more=team.querySelector('#team-show-all'),count=team.querySelector('#team-result-count');
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  let group='all',expanded=false;const initialCount=12;
  const render=animate=>{
   const matches=cards.filter(c=>group==='all'||c.dataset.teamGroup===group);
   const shown=group==='all'&&!expanded?matches.slice(0,initialCount):matches;
   const set=new Set(shown);
   cards.forEach(card=>{
    const newlyVisible=card.hidden&&set.has(card);
    card.getAnimations?.().forEach(a=>a.cancel());card.hidden=!set.has(card);
    if(animate&&newlyVisible&&!reduced.matches&&card.animate){card.animate([{opacity:0,transform:'translateY(7px)'},{opacity:1,transform:'none'}],{duration:220,easing:'ease-out'});}
   });
   filters.forEach(b=>{const active=b.dataset.teamFilter===group;b.classList.toggle('is-selected',active);b.setAttribute('aria-pressed',String(active));});
   const label=group==='all'?'SEO profile previews':config.groups.find(g=>g.id===group)?.label+' profile previews';
   count.textContent=group==='all'?`Showing ${shown.length} of ${cards.length} ${label}`:`${shown.length} ${label}`;
   more.hidden=group!=='all';more.setAttribute('aria-expanded',String(expanded));
   more.querySelector('.ui-button-label').textContent=expanded?'Show fewer profiles':`View all ${cards.length} profiles`;
  };
  team.querySelectorAll('[data-team-enhancement]').forEach(e=>{e.hidden=false;});
  filters.forEach(b=>b.addEventListener('click',()=>{group=b.dataset.teamFilter;expanded=false;render(true);}));
  // Arrow-key movement complements normal Tab navigation for the filter group.
  team.querySelector('.ab-team-filters').addEventListener('keydown',event=>{
   if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;
   const current=filters.indexOf(document.activeElement);if(current<0)return;
   event.preventDefault();let next=current;
   if(event.key==='Home')next=0;else if(event.key==='End')next=filters.length-1;
   else next=(current+(event.key==='ArrowRight'?1:-1)+filters.length)%filters.length;
   filters[next].focus();filters[next].click();
  });
  more.addEventListener('click',()=>{
   const collapse=expanded;expanded=!expanded;render(true);
   if(collapse&&team.getBoundingClientRect().top<-80){team.querySelector('.ab-team-toolbar').scrollIntoView({behavior:reduced.matches?'instant':'smooth',block:'start'});}
  });
  team.addEventListener('click',event=>{
   const trigger=event.target.closest('[data-team-profile]');if(!trigger)return;
   const p=profiles.get(trigger.dataset.teamProfile);if(!p)return;
   const content=el('div','ab-role-profile');
   const intro=el('div','ab-role-profile-intro'),img=el('img');img.src=p.image;img.alt='AI-generated sample portrait; not a confirmed employee';img.width=85;img.height=85;
   const copy=el('div');copy.append(el('p','ab-role-kicker',p.specialism),el('p','',p.summary));intro.append(img,copy);content.append(intro,el('h3','','Example responsibilities'));
   const tasks=el('ul','ab-role-tasks');p.responsibilities.forEach(task=>{const li=el('li');li.append(icon('check'),el('span','',task));tasks.append(li);});content.append(tasks);
   content.append(el('p','ab-role-preview','Illustrative role profile. This sample portrait does not identify a confirmed employee. Add the approved person’s name, photograph and responsibilities before publishing.'));
   const button=el('button','button ui-button');button.type='button';button.dataset.audit='';button.dataset.auditService=p.group==='local'?'Local SEO':p.group==='ai'?'AI SEO Services':'SEO Services';button.dataset.auditProject='About Us — '+p.role+' enquiry';button.append(el('span','ui-button-label','Discuss your SEO'),icon('angle-right'));
   button.addEventListener('click',()=>{const f=document.getElementById('audit-form');if(f){f.elements.selected_plan.value='';f.elements.plan_guide_rate.value='';}});
   content.append(button);document.dispatchEvent(new CustomEvent('grp:information',{detail:{title:p.role,content,trigger}}));
  });
  render(false);
 }
 root.querySelector('[data-careers-interest]')?.addEventListener('click',event=>{
  const trigger=event.currentTarget;trigger.dataset.audit='';trigger.dataset.auditService='Not sure yet';trigger.dataset.auditProject='Team enquiry — SEO roles at Google Ranker Pro';
 });
 root.querySelectorAll('[data-about-enquiry]').forEach(button=>button.addEventListener('click',()=>{
  const form=document.getElementById('audit-form');if(!form)return;
  form.elements.service.value='Not sure yet';form.elements.selected_plan.value='';form.elements.plan_guide_rate.value='';button.dataset.auditProject='About Us — '+button.dataset.aboutEnquiry;
 }));
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
