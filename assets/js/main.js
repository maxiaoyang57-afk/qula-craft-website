(function(){
  const navToggle=document.querySelector('[data-nav-toggle]');
  const nav=document.querySelector('[data-nav-menu]');
  if(navToggle&&nav){navToggle.addEventListener('click',()=>nav.classList.toggle('open'));}
  const topBtn=document.querySelector('[data-back-top]');
  window.addEventListener('scroll',()=>{if(topBtn)topBtn.classList.toggle('show',window.scrollY>560)},{passive:true});
  if(topBtn){topBtn.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));}

  // URL 参数预填询盘意向
  const params=new URLSearchParams(location.search);
  const product=params.get('product'); const application=params.get('application');
  if(product||application){document.querySelectorAll('.quote-form textarea').forEach(t=>{if(!t.value)t.value=(product?'Product interest: '+product+'\n':'')+(application?'Application: '+application+'\n':'');});}

  // 表单真提交(FormSubmit POST),仅做按钮状态反馈
  document.querySelectorAll('[data-quote-form]').forEach(form=>{
    form.addEventListener('submit',()=>{
      const btn=form.querySelector('button[type="submit"]');
      if(btn){btn.disabled=true;btn.textContent='Sending…';}
    });
  });

  // 产品目录筛选:标签页 + 复选框 + 实时计数
  const cards=document.querySelectorAll('.product-card[data-title]');
  const tabs=document.querySelectorAll('.tabs button');
  if(cards.length&&tabs.length){
    const boxes=document.querySelectorAll('.filter-card input[type="checkbox"]');
    const count=document.querySelector('[data-count]');
    let activeTab='all products';
    const key=label=>{const w=(label.toLowerCase().match(/[a-z]{4,}/g)||[]);return w[0]||label.toLowerCase();};
    function apply(){
      const checked=[...boxes].filter(b=>b.checked).map(b=>key(b.parentElement.textContent));
      let shown=0;
      cards.forEach(c=>{
        const hay=((c.dataset.title||'')+' '+(c.dataset.type||'')+' '+(c.dataset.use||'')).toLowerCase();
        const tabOk=activeTab==='all products'||hay.includes(activeTab);
        const boxOk=!checked.length||checked.some(k=>hay.includes(k));
        const show=tabOk&&boxOk;
        c.style.display=show?'':'none'; if(show)shown++;
      });
      if(count)count.textContent='Showing '+shown+' of '+cards.length+' items';
    }
    tabs.forEach(t=>t.addEventListener('click',()=>{
      tabs.forEach(x=>x.classList.remove('active'));t.classList.add('active');
      activeTab=t.textContent.trim().toLowerCase();apply();
    }));
    boxes.forEach(b=>b.addEventListener('change',apply));
    apply();
  }
})();

// products hub 实时搜索(目录内全部 SKU, 让 WebSite SearchAction 为真)
(function(){
  const sInput=document.querySelector('[data-catalog-search]');
  if(!sInput)return;
  const results=document.querySelector('[data-search-results]');
  const countEl=document.querySelector('[data-search-count]');
  const catGrid=document.querySelector('.category-grid');
  let items=null,tmr;
  const ST={'With':1,'And':1,'For':1,'Of':1,'The':1,'A':1,'An':1,'In':1,'On':1,'Per':1,'By':1,'To':1};
  const clean=t=>{let w=t.replace('Wight','Weight').replace('Breads','Beads').replace('Artfcal','Artificial').split(' ');while(w.length&&ST[w[w.length-1]])w.pop();return w.join(' ');};
  function card(p){
    const t=clean(p.title);
    const q=encodeURIComponent(p.sku+' '+t.slice(0,42));
    const waText=encodeURIComponent('Hello Qula Craft, I just viewed SKU '+p.sku+' and would like to discuss a custom quote. Can we chat?');
    return '<article class="product-card"><div class="product-img">'+(p.pdp?'<a href="'+p.pdp+'" style="display:block">':'')+'<img loading="lazy" src="'+p.image+'" alt="'+p.imageAlt+'" width="'+p.imageWidth+'" height="'+p.imageHeight+'">'+(p.pdp?'</a>':'')+'</div><div class="product-info"><span class="pill soft">'+p.sku+'</span><h3>'+(p.pdp?'<a href="'+p.pdp+'" style="color:inherit;text-decoration:none">'+t+'</a>':t)+'</h3><a class="btn btn-card" href="quote.html?product='+q+'">Send Inquiry <span>→</span></a><div class="card-cta-row"><a class="wa-line" href="https://wa.me/8618632026595?text='+waText+'" target="_blank" rel="noopener">WhatsApp</a><a class="basket-add" data-sku="'+p.sku+'" data-image="'+p.image+'">＋ Inquiry list</a></div></div></article>';
  }
  async function load(){
    if(items)return items;
    const j=await (await fetch('assets/data/product-catalog.json')).json();
    items=[];j.categories.forEach(c=>c.products.forEach(p=>items.push(p)));
    return items;
  }
  async function run(){
    const q=sInput.value.trim().toLowerCase();
    if(!q){results.hidden=true;results.innerHTML='';if(catGrid)catGrid.style.display='';countEl.textContent='';return;}
    const list=(await load()).filter(p=>(p.sku+' '+p.title+' '+p.category).toLowerCase().indexOf(q)>-1).slice(0,60);
    results.innerHTML=list.map(card).join('');
    results.hidden=false;if(catGrid)catGrid.style.display='none';
    countEl.textContent=list.length?('Showing '+list.length+' matching item'+(list.length>1?'s':'')):'No match — try a theme word like "pumpkin", "heart" or a SKU code';
  }
  sInput.addEventListener('input',()=>{clearTimeout(tmr);tmr=setTimeout(run,160);});
  const pre=new URLSearchParams(location.search).get('search');
  if(pre){sInput.value=pre;run();}
})();

// 询盘篮 Quote Basket(localStorage,多SKU一次询价)
(function(){
  const KEY='qcBasket';
  const load=()=>{try{return JSON.parse(localStorage.getItem(KEY)||'[]');}catch(e){return[];}};
  const save=l=>localStorage.setItem(KEY,JSON.stringify(l));
  // 浮动篮 chip(全站)
  const chip=document.createElement('a');
  chip.className='basket-chip';chip.href='quote.html';
  chip.innerHTML='Inquiry list <b>0</b>';
  document.body.appendChild(chip);
  function renderChip(){
    const n=load().length;
    chip.querySelector('b').textContent=n;
    chip.classList.toggle('on',n>0);
  }
  renderChip();
  function imageFromButton(a){
    const scopes=[a.closest('.product-card'),a.closest('.detail-grid'),a.closest('.product-info'),document];
    let src=a.dataset.image||new URLSearchParams(location.search).get('image')||'';
    for(const scope of scopes){
      if(src||!scope)continue;
      const img=scope.querySelector('.product-img img,.gallery-main img,img');
      src=img&&img.getAttribute('src')||'';
    }
    return src.trim();
  }
  let catalogImages=null;
  async function loadCatalogImages(){
    if(catalogImages)return catalogImages;
    catalogImages={};
    try{
      const j=await (await fetch('assets/data/product-catalog.json')).json();
      (j.categories||[]).forEach(c=>(c.products||[]).forEach(p=>{if(p.sku&&!catalogImages[p.sku])catalogImages[p.sku]=p.image||'';}));
    }catch(e){}
    return catalogImages;
  }
  function normalizeList(list){
    let changed=false;
    const out=list.map(x=>{
      if(x&&x.sku&&!x.image){
        const btn=[...document.querySelectorAll('.basket-add')].find(a=>a.dataset.sku===x.sku);
        if(btn){x.image=imageFromButton(btn);changed=true;}
        else if(catalogImages&&catalogImages[x.sku]){x.image=catalogImages[x.sku];changed=true;}
      }
      return x;
    });
    if(changed)save(out);
    return out;
  }
  // 加入篮(事件委托,含 JS 搜索结果卡)
  document.addEventListener('click',e=>{
    const a=e.target.closest&&e.target.closest('.basket-add');
    if(!a||a.classList.contains('added'))return;
    const list=normalizeList(load());
    if(!list.some(x=>x.sku===a.dataset.sku)){
      list.push({sku:a.dataset.sku,image:imageFromButton(a)});
      save(list);
    }
    a.classList.add('added');a.textContent='✓ In list';
    renderChip();
  });
  // 已在篮中的按钮标记
  document.querySelectorAll('.basket-add').forEach(a=>{
    if(load().some(x=>x.sku===a.dataset.sku)){a.classList.add('added');a.textContent='✓ In list';}
  });
  // quote 页:渲染篮面板 + 预填 textarea
  if(/quote\.html$/.test(location.pathname)){
    const form=document.querySelector('.quote-form-v2, .quote-form');
    const ta=form?form.querySelector('textarea[name="message"], textarea'):null;
    function syncTa(){
      const list=normalizeList(load());
      if(!ta)return;
      const block=list.length?('Inquiry list:\n'+list.map(x=>'- '+x.sku).join('\n')+'\n'):'';
      const rest=ta.value.replace(/^Inquiry list:[\s\S]*?\n(?=\S|$)/,'').replace(/^Inquiry list:[\s\S]*$/,'');
      ta.value=block+rest;
    }
    async function renderPanel(){
      await loadCatalogImages();
      let p=document.querySelector('.basket-panel');
      const list=normalizeList(load());
      if(!list.length){if(p)p.remove();syncTa();renderChip();return;}
      if(!p){
        p=document.createElement('div');p.className='basket-panel';
        form.insertBefore(p, form.firstChild);
      }
      const esc=s=>String(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
      p.innerHTML='<h3>Your inquiry list ('+list.length+') <span class="bp-clear" data-clear>clear all</span></h3><ul>'+
        list.map(x=>'<li><span class="bp-item"><img src="'+esc(x.image||'assets/images/favicon.png')+'" alt="'+esc(x.sku)+'" loading="lazy"><b>'+esc(x.sku)+'</b></span><span class="bp-remove" data-sku="'+esc(x.sku)+'">×</span></li>').join('')+'</ul>';
      syncTa();renderChip();
    }
    document.addEventListener('click',e=>{
      if(e.target.dataset&&e.target.dataset.sku&&e.target.classList.contains('bp-remove')){
        save(load().filter(x=>x.sku!==e.target.dataset.sku));renderPanel();
      }
      if(e.target.dataset&&'clear'in e.target.dataset){save([]);renderPanel();}
    });
    renderPanel();
    if(form)form.addEventListener('submit',()=>{save([]);});
  }
})();
