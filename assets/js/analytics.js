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
  // 询盘表单提交 → generate_lead
  document.addEventListener('submit',function(e){
    var f=e.target;
    if(f&&f.getAttribute&&(f.getAttribute('action')||'').indexOf('formsubmit')>-1){
      gtag('event','generate_lead',{page:location.pathname});
    }
  },true);
})();
