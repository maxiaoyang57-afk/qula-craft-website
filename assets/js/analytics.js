/* Qula Craft GA4 — property 549323595 / web stream 15412253402 */
(function(){
  var GA_ID='G-KKT7E44TD2';
  window.dataLayer=window.dataLayer||[];
  function gtag(){dataLayer.push(arguments);}window.gtag=gtag;
  gtag('js',new Date());gtag('config',GA_ID);
  // CWV 保护:load 后延迟 1.2s 注入 gtag 脚本(事件在此之前已进 dataLayer 队列)
  function inject(){
    var s=document.createElement('script');s.async=true;
    s.src='https://www.googletagmanager.com/gtag/js?id='+GA_ID;
    document.head.appendChild(s);
  }
  if(document.readyState==='complete'){setTimeout(inject,1200);}
  else{window.addEventListener('load',function(){setTimeout(inject,1200);});}
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

  document.addEventListener('submit',function(e){
    var f=e.target;
    if(f&&f.getAttribute&&(f.getAttribute('action')||'').indexOf('formsubmit')>-1){
      gtag('event','inquiry_submit_attempt',{page:location.pathname,form_id:f.id||''});
      if(f.id!=='inquiryForm'&&f.id!=='inquiryFormHome') markPendingInquiry(f);
    }
  },true);

  if(/\/thank-you\.html$/.test(location.pathname)){
    try{
      var pending=JSON.parse(sessionStorage.getItem(LEAD_MARKER)||'null');
      if(pending&&Number.isFinite(pending.ts)&&Date.now()-pending.ts>=0&&Date.now()-pending.ts<=30*60*1000){
        sessionStorage.removeItem(LEAD_MARKER);
        var params={
          page:pending.page||'',
          confirmation_page:location.pathname,
          form_id:pending.form_id||'',
          lead_type:'wholesale_inquiry',
          lead_status:'accepted'
        };
        // One confirmed thank-you return equals one GA4 lead conversion.
        gtag('event','generate_lead',params);
      }
    }catch(e){
      try{sessionStorage.removeItem(LEAD_MARKER);}catch(_){}
    }
  }
})();