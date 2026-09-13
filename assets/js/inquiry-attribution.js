/*
 * Adds a compact, non-sensitive acquisition record to every FormSubmit inquiry.
 * The record is sent only when a buyer chooses to submit a form. It helps sales
 * distinguish organic search, paid campaigns, social referrals and AI referrals
 * without adding a third-party tracker or changing the inquiry recipient.
 */
(function () {
  var STORAGE_KEY = 'qulaInquiryAttributionV1';
  var CAMPAIGN_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'msclkid', 'fbclid'];
  var AI_HOSTS = ['chatgpt.com', 'perplexity.ai', 'claude.ai', 'copilot.microsoft.com', 'gemini.google.com', 'you.com'];

  function safeUrl(value) {
    try {
      var url = new URL(value);
      return url.protocol === 'http:' || url.protocol === 'https:' ? url : null;
    } catch (error) {
      return null;
    }
  }

  function hostLabel(host) {
    host = (host || '').toLowerCase();
    if (!host) return 'Direct / unknown';
    if (AI_HOSTS.some(function (known) { return host === known || host.endsWith('.' + known); })) return 'AI referral';
    if (host.indexOf('google.') > -1) return 'Google organic';
    if (host.indexOf('bing.com') > -1) return 'Bing organic';
    if (host.indexOf('yahoo.') > -1 || host.indexOf('duckduckgo.') > -1) return 'Search referral';
    if (host.indexOf('linkedin.') > -1) return 'LinkedIn referral';
    if (host.indexOf('facebook.') > -1 || host.indexOf('instagram.') > -1) return 'Meta referral';
    if (host.indexOf('pinterest.') > -1) return 'Pinterest referral';
    if (host.indexOf('youtube.') > -1 || host.indexOf('tiktok.') > -1) return 'Video / social referral';
    return 'Referral';
  }

  function truncate(value, length) {
    return String(value || '').slice(0, length);
  }

  function readStored() {
    try {
      var raw = window.sessionStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (error) {
      return null;
    }
  }

  function buildAttribution() {
    var params = new URL(window.location.href).searchParams;
    var campaign = {};
    CAMPAIGN_KEYS.forEach(function (key) {
      var value = params.get(key);
      if (value) campaign[key] = truncate(value, 160);
    });

    var referrerUrl = safeUrl(document.referrer);
    var landing = window.location.href;
    var source = campaign.gclid ? 'Google Ads' : campaign.msclkid ? 'Microsoft Ads' : campaign.fbclid ? 'Meta Ads' : campaign.utm_source ? 'Campaign: ' + campaign.utm_source : hostLabel(referrerUrl && referrerUrl.hostname);

    return {
      source: source,
      landingPage: truncate(landing, 1000),
      referrer: referrerUrl ? truncate(referrerUrl.href, 1000) : 'Direct / unavailable',
      campaign: Object.keys(campaign).length ? JSON.stringify(campaign) : 'None',
      recordedAt: new Date().toISOString()
    };
  }

  var attribution = readStored() || buildAttribution();
  try { window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(attribution)); } catch (error) {}

  function addField(form, name, value) {
    var field = form.querySelector('input[name="' + name + '"]');
    if (!field) {
      field = document.createElement('input');
      field.type = 'hidden';
      field.name = name;
      form.appendChild(field);
    }
    field.value = value;
  }

  function annotateForm(form) {
    addField(form, 'Inquiry source', attribution.source);
    addField(form, 'Landing page', attribution.landingPage);
    addField(form, 'Referrer', attribution.referrer);
    addField(form, 'Campaign parameters', attribution.campaign);
    addField(form, 'Inquiry page', truncate(window.location.href, 1000));
  }

  document.querySelectorAll('form[action^="https://formsubmit.co/"]').forEach(annotateForm);
}());
