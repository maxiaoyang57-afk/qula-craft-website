/* Qula Craft GA4 — property 549323595 / web stream 15412253402 */
(function(){
  var GA_ID='G-KKT7E44TD2';
  var IS_CANONICAL_ANALYTICS_HOST=/^(www\.)?qulacrafts\.com$/i.test(window.location.hostname);
  if(!IS_CANONICAL_ANALYTICS_HOST)return;
  // Clarity consent adapter: no SDK request before an explicit analytics choice.
  function createClarityConsent(projectId, eligible) {
    let loaded = false;
    let stopped = false;
    let allowed = false;
    const events = new Set(['generate_lead', 'inquiry_submit_attempt', 'whatsapp_click', 'email_click', 'phone_click', 'quote_click', 'product_click']);
    const privacySignal = () => window.navigator.globalPrivacyControl === true || window.navigator.doNotTrack === '1';
    const maskForms = (root) => {
      const selector = 'form, [contenteditable], [data-inquiry-summary], [data-upload-preview]';
      if (root.matches && root.matches(selector)) root.setAttribute('data-clarity-mask', 'true');
      if (root.querySelectorAll) root.querySelectorAll(selector).forEach((node) => node.setAttribute('data-clarity-mask', 'true'));
    };
    const update = (value) => {
      allowed = value === 'granted' && eligible && !privacySignal();
      if (!allowed) {
        if (loaded && typeof window.clarity === 'function') {
          window.clarity('consentv2', { analytics_Storage: 'denied', ad_Storage: 'denied' });
          window.clarity('stop');
          stopped = true;
        }
        return;
      }
      // A withdrawn recording stays stopped in this document. A fresh page can
      // start a new consented session, without reloading an unfinished inquiry.
      if (stopped) return;
      if (!loaded) {
        maskForms(document);
        if (typeof MutationObserver === 'function') {
          new MutationObserver((records) => records.forEach((record) => record.addedNodes.forEach(maskForms)))
            .observe(document.documentElement, { childList: true, subtree: true });
        }
        window.clarity = window.clarity || function () {
          (window.clarity.q = window.clarity.q || []).push(arguments);
        };
        window.clarity('consentv2', { analytics_Storage: 'granted', ad_Storage: 'denied' });
        const script = document.createElement('script');
        script.async = true;
        script.dataset.sdk = 'clarity';
        script.src = 'https://www.clarity.ms/tag/' + projectId;
        document.head.appendChild(script);
        loaded = true;
      } else {
        window.clarity('consentv2', { analytics_Storage: 'granted', ad_Storage: 'denied' });
      }
    };
    return {
      update,
      event: (name) => {
        if (allowed && loaded && !stopped && events.has(name)) window.clarity('event', name);
      }
    };
  }
  // End Clarity consent adapter.
  var CONSENT_KEY='qula_analytics_consent_v1';
  function readConsent(){try{return window.localStorage.getItem(CONSENT_KEY);}catch(e){return null;}}
  function consentState(value){return {analytics_storage:value==='granted'?'granted':'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'};}
  var clarityConsent=createClarityConsent('y5ull9s9j6',IS_CANONICAL_ANALYTICS_HOST);
  window.dataLayer=window.dataLayer||[];
  function gtag(){window.dataLayer.push(arguments);if(arguments[0]==='event')clarityConsent.event(arguments[1]);}window.gtag=gtag;
  gtag('consent','default',consentState('denied'));
  if(readConsent()==='granted')gtag('consent','update',consentState('granted'));
  gtag('js',new Date());gtag('config',GA_ID,{allow_google_signals:false,allow_ad_personalization_signals:false});
  clarityConsent.update(readConsent());
  function applyConsent(value){
    try{window.localStorage.setItem(CONSENT_KEY,value);}catch(e){}
    gtag('consent','update',consentState(value));
    clarityConsent.update(value);
  }
  window.addEventListener('storage',function(event){
    if(event.key===CONSENT_KEY||event.key===null){
      gtag('consent','update',consentState(readConsent()));
      clarityConsent.update(readConsent());
    }
  });
  function mountConsent(){
    if(document.getElementById('qula-analytics-consent'))return;
    var css=document.createElement('link');css.rel='stylesheet';css.href='/assets/css/analytics-consent.css?v=20261014';document.head.appendChild(css);
    var panel=document.createElement('section');panel.id='qula-analytics-consent';panel.className='qc-consent';
    panel.setAttribute('role','dialog');panel.setAttribute('aria-labelledby','qc-consent-title');panel.setAttribute('aria-describedby','qc-consent-description');
    panel.innerHTML='<div><strong id="qc-consent-title">Help us improve Qula Craft</strong><p id="qc-consent-description">We use Google Analytics for website statistics and Microsoft Clarity for heatmaps and session replay. Analytics cookies and Clarity recordings are enabled only if you accept. Inquiry form content is masked. <a href="/privacy-policy.html">Privacy policy</a></p></div><div class="qc-consent-actions"><button type="button" data-analytics-decline>Decline analytics</button><button type="button" data-analytics-accept>Accept analytics</button></div>';
    panel.hidden=readConsent()!==null;document.body.appendChild(panel);
    var reopen=document.createElement('button');reopen.type='button';reopen.className='qc-cookie-settings';reopen.textContent='Cookie choices';
    var footer=document.querySelector('footer .container')||document.querySelector('footer')||document.body;footer.appendChild(reopen);
    reopen.addEventListener('click',function(){panel.hidden=false;panel.querySelector('[data-analytics-decline]').focus();});
    function choose(value){applyConsent(value);panel.hidden=true;reopen.focus({preventScroll:true});}
    panel.querySelector('[data-analytics-accept]').addEventListener('click',function(){choose('granted');});
    panel.querySelector('[data-analytics-decline]').addEventListener('click',function(){choose('denied');});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mountConsent,{once:true});else mountConsent();
  // CWV 保护:load 后延迟 1.2s 注入 gtag 脚本(事件在此之前已进 dataLayer 队列)
  function inject(){
    var s=document.createElement('script');s.async=true;
    s.src='https://www.googletagmanager.com/gtag/js?id='+GA_ID;
    document.head.appendChild(s);
  }
  if(document.readyState==='complete'){setTimeout(inject,1200);}
  else{window.addEventListener('load',function(){setTimeout(inject,1200);});}
  // Measure internal buying steps only after an explicit analytics choice.
  // Delegation also covers search results inserted after page load. Never send
  // link text, inquiry parameters, hashes, or a customer-entered product name.
  document.addEventListener('click',function(e){
    if(readConsent()!=='granted'||window.navigator.globalPrivacyControl===true||window.navigator.doNotTrack==='1')return;
    var link=e.target&&e.target.closest?e.target.closest('a[href]'):null;
    if(!link)return;
    var target;
    try{target=new URL(link.getAttribute('href'),location.href);}catch(error){return;}
    if(!/^https?:$/.test(target.protocol)||target.username||target.password||target.port||!/^(www\.)?qulacrafts\.com$/i.test(target.hostname))return;
    var name='';
    if(/^\/p-[a-z0-9][a-z0-9-]*\.html$/i.test(target.pathname))name='product_click';
    else if(target.pathname==='/quote.html')name='quote_click';
    if(!name)return;
    var area='content';
    if(link.closest('.mobile-cta-bar'))area='mobile_cta';
    else if(link.closest('header, nav'))area='navigation';
    else if(link.closest('footer'))area='footer';
    else if(link.closest('.product-card, .product-card-v2, [data-product-card]'))area='product_card';
    else if(link.closest('.pdp-cta, .page-hero, .hero'))area='hero';
    var source=/^\/[a-z0-9._/-]*$/i.test(location.pathname)?location.pathname:'/';
    gtag('event',name,{
      page_path:source,
      page_location:location.origin+source,
      destination_path:target.pathname,
      link_location:area
    });
  });
  // 转化事件:WhatsApp / 邮箱 / 电话点击
  document.addEventListener('click',function(e){
    var a=e.target&&e.target.closest?e.target.closest('a'):null;if(!a)return;
    var h=a.getAttribute('href')||'';
    if(h.indexOf('wa.me')>-1)gtag('event','whatsapp_click',{link_url:h});
    else if(h.indexOf('mailto:')===0)gtag('event','email_click',{link_url:h});
    else if(h.indexOf('tel:')===0)gtag('event','phone_click',{link_url:h});
  });
  // FormSubmit is cross-origin, so distinguish an attempt from a confirmed return.
  // Dedicated quote forms can abort after the submit event while preparing attachments;
  // those forms mark the pending inquiry only immediately before the native POST.
  var LEAD_MARKER='qula_pending_inquiry_v1';
  function markPendingInquiry(form){
    try{
      sessionStorage.setItem(LEAD_MARKER,JSON.stringify({
        ts:Date.now(),
        page:location.pathname,
        form_id:form&&form.id||''
      }));
    }catch(e){}
  }
  window.QULA_MARK_INQUIRY_PENDING=markPendingInquiry;
  window.QULA_CLEAR_INQUIRY_PENDING=function(){
    try{sessionStorage.removeItem(LEAD_MARKER);}catch(e){}
  };

  document.addEventListener('submit',function(e){
    var f=e.target;
    if(f&&f.getAttribute&&(f.getAttribute('action')||'').indexOf('formsubmit')>-1){
      gtag('event','inquiry_submit_attempt',{page:location.pathname,form_id:f.id||''});
      if(f.id!=='inquiryForm'&&f.id!=='inquiryFormHome') {
        // Wait for form handlers to finish before marking a native submission.
        queueMicrotask(function(){if(!e.defaultPrevented)markPendingInquiry(f);});
      }
    }
  },true);

  if(/\/thank-you\.html$/.test(location.pathname)){
    try{
      var pending=JSON.parse(sessionStorage.getItem(LEAD_MARKER)||'null');
      sessionStorage.removeItem(LEAD_MARKER);
      if(pending&&Number.isFinite(pending.ts)&&Date.now()-pending.ts>=0&&Date.now()-pending.ts<=30*60*1000){
        sessionStorage.removeItem(LEAD_MARKER);
        var params={
          page:pending.page||'',
          confirmation_page:location.pathname,
          form_id:pending.form_id||'',
          lead_type:'wholesale_inquiry',
          lead_status:'confirmed_return'
        };
        // One confirmed thank-you return equals one GA4 lead conversion.
        gtag('event','generate_lead',params);
      }
    }catch(e){
      try{sessionStorage.removeItem(LEAD_MARKER);}catch(_){}
    }
  }
})();
