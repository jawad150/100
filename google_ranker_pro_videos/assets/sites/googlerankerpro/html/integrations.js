/* Server-provided public IDs only. Provider credentials never belong in this file. */
(() => {
  'use strict';
  if (window.__grpIntegrationsReady) return;
  window.__grpIntegrationsReady = true;
  let config;
  try { config = JSON.parse(document.getElementById('grp-public-integrations')?.textContent || '{}'); }
  catch { return; }

  const ready = () => {
    const form = document.getElementById('newsletter-form');
    if (form) {
      const fieldset = form.querySelector('fieldset');
      const status = document.getElementById('newsletter-status');
      const email = document.getElementById('newsletter-email');
      const consent = document.getElementById('newsletter-consent');
      const submit = form.querySelector('[type="submit"]');
      let busy = false;
      if (fieldset) fieldset.disabled = false;
      if (status && config.newsletter) status.hidden = true;
      const message = text => {
        if (!status) return;
        status.hidden = false;
        status.textContent = text;
        status.dataset.state = 'notice';
      };
      // Capturing stops the supplied preview-only handler from also submitting.
      form.addEventListener('submit', async event => {
        event.preventDefault();
        event.stopImmediatePropagation();
        if (busy) return;
        if (!config.newsletter) { message('Newsletter subscription is not configured yet. No details have been sent.'); return; }
        if (!email || !consent || !form.reportValidity()) return;
        if (!consent.checked) { consent.focus(); return; }
        const csrf = document.querySelector('meta[name="csrf-token"]')?.content;
        if (!csrf) { message('Please refresh this page before subscribing.'); return; }
        busy = true;
        if (submit) submit.disabled = true;
        form.setAttribute('aria-busy', 'true');
        message('Requesting your confirmation email…');
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), 18000);
        try {
          const response = await fetch('/newsletter', {
            method: 'POST', credentials: 'same-origin', signal: controller.signal,
            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json', 'X-CSRF-TOKEN': csrf },
            body: JSON.stringify({
              email: email.value.trim(), consent: consent.checked,
              consentText: 'I agree to receive marketing emails from Google Ranker Pro.',
              source: 'website-footer', website: document.getElementById('newsletter-website')?.value || ''
            })
          });
          let result = {};
          try { result = await response.json(); } catch {}
          if (response.ok && result.status === 'pending_confirmation') {
            message('Check your inbox and confirm your email address to complete your subscription.');
            form.reset();
          } else if (response.status === 422) {
            message('Please enter a valid email address and agree to receive marketing emails.');
          } else if (response.status === 419) {
            message('Your page has expired. Please refresh it and try again.');
          } else {
            message(result.message || 'Subscription is temporarily unavailable. Please try again later.');
          }
        } catch {
          message('We could not confirm whether your request was received. Please check your inbox before trying again in a few minutes.');
        } finally {
          clearTimeout(timer);
          busy = false;
          if (submit) submit.disabled = false;
          form.removeAttribute('aria-busy');
        }
      }, true);
    }

    const ga4 = /^G-[A-Z0-9]+$/.test(config.ga4 || '') ? config.ga4 : '';
    const gtm = /^GTM-[A-Z0-9]+$/.test(config.gtm || '') ? config.gtm : '';
    if (!config.tracking || Boolean(ga4) === Boolean(gtm)) return;

    // A provider change requires a fresh choice. Never use advanced consent pings.
    const storageKey = 'grp.analytics.consent.v1';
    const version = `2026-10-22:${ga4 || gtm}`;
    let choice = null;
    let loaded = false;
    let opener = null;
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey) || 'null');
      if (saved?.version === version && saved.expires > Date.now() && typeof saved.allowed === 'boolean') choice = saved.allowed;
    } catch {}
    window.dataLayer = window.dataLayer || [];
    const gtag = function () { window.dataLayer.push(arguments); };
    gtag('consent', 'default', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });

    const load = () => {
      if (loaded || choice !== true) return;
      loaded = true;
      gtag('consent', 'update', { analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
      const script = document.createElement('script');
      script.async = true;
      script.dataset.grpAnalytics = 'true';
      if (ga4) {
        window[`ga-disable-${ga4}`] = false;
        gtag('js', new Date());
        gtag('config', ga4, { allow_google_signals: false, allow_ad_personalization_signals: false, page_location: location.origin + location.pathname });
        script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(ga4)}`;
      } else {
        window.dataLayer.push({ 'gtm.start': Date.now(), event: 'gtm.js' });
        script.src = `https://www.googletagmanager.com/gtm.js?id=${encodeURIComponent(gtm)}`;
      }
      document.head.append(script);
    };
    const clearAnalyticsCookies = () => {
      const domains = [null, location.hostname, `.${location.hostname}`];
      const parts = location.hostname.split('.');
      for (let i = 1; i < parts.length - 1; i++) domains.push(`.${parts.slice(i).join('.')}`);
      for (const cookie of document.cookie.split(';')) {
        const name = cookie.split('=')[0].trim();
        if (!/^(_ga(?:_|$)|_gid$|_gat(?:_|$)|_gcl_)/.test(name)) continue;
        for (const domain of domains) document.cookie = `${name}=; Max-Age=0; Path=/; SameSite=Lax${domain ? `; Domain=${domain}` : ''}`;
      }
    };

    const style = document.createElement('style');
    style.textContent = '#grp-cookie-preferences{position:fixed;z-index:2147483000;bottom:20px;left:20px;right:20px;max-width:680px;margin:auto;background:#fff;color:#152338;border:1px solid #a7b4c8;border-radius:16px;box-shadow:0 12px 45px #15233830;padding:22px;font:16px/1.5 system-ui,sans-serif}#grp-cookie-preferences[hidden]{display:none}#grp-cookie-preferences h2{font:700 20px/1.3 system-ui,sans-serif;margin:0 0 8px;color:#152338}#grp-cookie-preferences p{margin:0 0 14px;color:#33445c}#grp-cookie-preferences a{color:#154fc0;text-decoration:underline}#grp-cookie-preferences .grp-cookie-actions{display:flex;flex-wrap:wrap;gap:10px}#grp-cookie-preferences button{font:600 15px/1.4 system-ui,sans-serif;padding:10px 16px;background:#152338;color:#fff;border:2px solid #152338;border-radius:8px;cursor:pointer}#grp-cookie-preferences button:focus-visible{outline:3px solid #f17736;outline-offset:3px}#grp-cookie-preferences .grp-cookie-close{background:#fff;color:#152338}#grp-cookie-toggle{position:fixed;bottom:12px;left:12px;z-index:1000;background:#fff;color:#152338;border:1px solid #8391a6;border-radius:8px;padding:8px 12px;font:14px/1.4 system-ui,sans-serif;cursor:pointer}';
    document.head.append(style);
    const panel = document.createElement('section');
    panel.id = 'grp-cookie-preferences';
    panel.hidden = true;
    panel.setAttribute('role', 'region');
    panel.setAttribute('aria-labelledby', 'grp-cookie-title');
    panel.innerHTML = '<h2 id="grp-cookie-title">Your privacy choices</h2><p>Essential cookies keep this website working. With your permission, Google Analytics helps us understand website usage. Analytics is optional. You can change your choice at any time. <a href="/cookie-policy.html">Read our cookie policy</a>.</p><div class="grp-cookie-actions"><button type="button" data-grp-choice="false">Essential only</button><button type="button" data-grp-choice="true">Allow analytics</button><button type="button" class="grp-cookie-close" data-grp-close>Close</button></div>';
    document.body.append(panel);
    const status = () => {
      const node = document.getElementById('sp-cookie-status');
      if (node) node.textContent = choice === true ? 'Analytics allowed. Use Cookie settings to withdraw consent.' : 'Optional analytics is off. Essential cookies only.';
    };
    const close = () => { panel.hidden = true; if (opener?.isConnected) opener.focus(); };
    const open = trigger => { opener = trigger || null; panel.hidden = false; if (trigger) panel.querySelector('button').focus(); };
    const choose = allowed => {
      const wasLoaded = loaded;
      choice = allowed;
      try { localStorage.setItem(storageKey, JSON.stringify({ version, allowed, expires: Date.now() + 180 * 86400000 })); } catch {}
      status();
      close();
      if (allowed) { load(); return; }
      if (ga4) window[`ga-disable-${ga4}`] = true;
      gtag('consent', 'update', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
      clearAnalyticsCookies();
      document.querySelectorAll('script[data-grp-analytics]').forEach(script => script.remove());
      // Reload removes already executing tags, including an accepted GTM container.
      if (wasLoaded) location.reload();
    };
    panel.addEventListener('click', event => {
      const button = event.target.closest('[data-grp-choice]');
      if (button) choose(button.dataset.grpChoice === 'true');
      else if (event.target.closest('[data-grp-close]')) close();
    });
    panel.addEventListener('keydown', event => { if (event.key === 'Escape') close(); });
    let controls = document.querySelectorAll('[data-cookie-settings]');
    if (!controls.length) {
      const toggle = document.createElement('button');
      toggle.type = 'button'; toggle.id = 'grp-cookie-toggle'; toggle.dataset.cookieSettings = ''; toggle.textContent = 'Cookie settings';
      document.body.append(toggle);
      controls = [toggle];
    }
    controls.forEach(button => { button.removeAttribute('aria-haspopup'); button.setAttribute('aria-controls', panel.id); });
    // Capture prevents the legacy empty-provider cookie dialog from also opening.
    document.addEventListener('click', event => {
      const button = event.target.closest('[data-cookie-settings]');
      if (!button) return;
      event.preventDefault(); event.stopImmediatePropagation(); open(button);
    }, true);
    window.addEventListener('storage', event => {
      if (event.key === storageKey) location.reload();
    });
    status();
    if (choice === true) load();
    else { clearAnalyticsCookies(); if (choice === null) open(null); }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready, { once: true });
  else ready();
})();
