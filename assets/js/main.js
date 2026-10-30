(function(){
  const navToggle=document.querySelector('[data-nav-toggle]');
  const nav=document.querySelector('[data-nav-menu]');
  if(navToggle&&nav){navToggle.addEventListener('click',()=>nav.classList.toggle('open'));}
  const topBtn=document.querySelector('[data-back-top]');
  window.addEventListener('scroll',()=>{if(topBtn)topBtn.classList.toggle('show',window.scrollY>560)},{passive:true});
  if(topBtn){topBtn.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));}

  // Official Qula Craft video channel: keep a visible, consistent link on every page.
  const youtubeChannel='https://www.youtube.com/channel/UCKeqaiZQYSMGdKvRAcLMnJQ';
  const youtubeIcon='<svg viewBox="0 0 24 24" width="19" height="19" aria-hidden="true" focusable="false"><path fill="currentColor" d="M23.5 6.2a3 3 0 0 0-2.1-2.12C19.55 3.58 12 3.58 12 3.58s-7.55 0-9.4.5A3 3 0 0 0 .5 6.2C0 8.07 0 12 0 12s0 3.93.5 5.8a3 3 0 0 0 2.1 2.12c1.85.5 9.4.5 9.4.5s7.55 0 9.4-.5a3 3 0 0 0 2.1-2.12C24 15.93 24 12 24 12s0-3.93-.5-5.8ZM9.6 15.63V8.37L15.87 12 9.6 15.63Z"/></svg>';
  const youtubeLink=(label,extraClass)=>{
    const link=document.createElement('a');
    link.className='youtube-cta '+(extraClass||'');
    link.dataset.qulaYoutube='true';
    link.href=youtubeChannel;
    link.target='_blank';
    link.rel='noopener noreferrer';
    link.setAttribute('aria-label',label+' on Qula Craft YouTube');
    link.innerHTML=youtubeIcon+'<span>'+label+'</span>';
    return link;
  };
  document.querySelectorAll('.footer').forEach(footer=>{
    const heading=[...footer.querySelectorAll('h4')].find(h=>h.textContent.trim()==='Contact');
    const contactColumn=heading&&heading.parentElement;
    if(!contactColumn||contactColumn.querySelector('[data-qula-youtube]'))return;
    const line=document.createElement('p');
    line.className='contact-line youtube-contact';
    line.append(youtubeLink('Watch Qula Craft Videos','youtube-cta--footer'));
    contactColumn.insertBefore(line,contactColumn.querySelector('a.btn')||null);
  });
  document.querySelectorAll('.pcraft-actions').forEach(actions=>{
    if(!actions.querySelector('[data-qula-youtube]'))actions.append(youtubeLink('Watch Our Videos','youtube-cta--home'));
  });
  document.querySelectorAll('.pdp-cta').forEach(cta=>{
    if(!cta.querySelector('[data-qula-youtube]'))cta.append(youtubeLink('Watch Product Videos','youtube-cta--pdp'));
  });

  // URL 参数预填询盘意向
  const params=new URLSearchParams(location.search);
  const product=params.get('product'); const application=params.get('application');
  if(product||application){document.querySelectorAll('.quote-form textarea').forEach(t=>{if(!t.value)t.value=(product?'Product interest: '+product+'\n':'')+(application?'Application: '+application+'\n':'');});}

  // 表单真提交(FormSubmit POST),仅做按钮状态反馈
  document.querySelectorAll('[data-quote-form]').forEach(form=>{
    const button=form.querySelector('button[type="submit"]');
    const idleText=button?.innerHTML;
    window.addEventListener('pageshow',()=>{if(button){button.disabled=false;button.innerHTML=idleText;}});
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
  const paging=document.querySelector('[data-search-controls]');
  const more=document.querySelector('[data-search-more]');
  const all=document.querySelector('[data-search-all]');
  let matches=[],shown=0;
  function show(limit,focusNew=false){
    const previous=shown;
    shown=Math.min(limit,matches.length);
    results.insertAdjacentHTML('beforeend',matches.slice(previous,shown).map(card).join(''));
    countEl.textContent=matches.length?('Showing '+shown+' of '+matches.length+' matching items'):'No match — try a theme word like "pumpkin", "heart" or a SKU code';
    if(paging)paging.hidden=shown>=matches.length;
    if(more)more.textContent='Show '+Math.min(24,matches.length-shown)+' more results';
    if(all)all.textContent='Show all '+matches.length+' results';
    if(focusNew){
      const first=results.querySelectorAll('.product-card')[previous];
      const link=first&&first.querySelector('a[href]');
      if(link){link.focus({preventScroll:true});first.scrollIntoView({block:'start',behavior:'auto'});}
    }
  }
  if(more)more.addEventListener('click',()=>show(shown+24,true));
  if(all)all.addEventListener('click',()=>show(matches.length,true));
  let items=null,loading=null,tmr,searchRevision=0;
  const ST={'With':1,'And':1,'For':1,'Of':1,'The':1,'A':1,'An':1,'In':1,'On':1,'Per':1,'By':1,'To':1};
  const clean=t=>{let w=t.replace('Wight','Weight').replace('Breads','Beads').replace('Artfcal','Artificial').split(' ');while(w.length&&ST[w[w.length-1]])w.pop();return w.join(' ');};
  function card(p){
    const t=clean(p.title);
    const q=encodeURIComponent(p.sku+' '+t.slice(0,42));
    const inquiryUrl=p.inquiryUrl||'quote.html?product='+q;
    const waText=encodeURIComponent('Hello Qula Craft, I just viewed SKU '+p.sku+' and would like to discuss a custom quote. Can we chat?');
    return '<article class="product-card"><div class="product-img">'+(p.pdp?'<a href="'+p.pdp+'" style="display:block">':'')+'<img loading="lazy" src="'+p.image+'" alt="'+p.imageAlt+'" width="'+p.imageWidth+'" height="'+p.imageHeight+'">'+(p.pdp?'</a>':'')+'</div><div class="product-info"><span class="pill soft">'+p.sku+'</span><h3>'+(p.pdp?'<a href="'+p.pdp+'" style="color:inherit;text-decoration:none">'+t+'</a>':t)+'</h3><a class="btn btn-card" href="'+inquiryUrl+'">Send Inquiry <span>→</span></a><div class="card-cta-row"><a class="wa-line" href="https://wa.me/8618632026595?text='+waText+'" target="_blank" rel="noopener">WhatsApp</a><button type="button" class="basket-add" data-sku="'+p.sku+'" data-image="'+p.image+'">＋ Inquiry list</button></div></div></article>';
  }
  async function load(){
    if(items)return items;
    // Every pending search can share one download without caching a failed request.
    if(!loading)loading=(async()=>{
      const response=await fetch('assets/data/product-catalog.json?v=20261018-extension');
      if(!response.ok)throw new Error('Catalog unavailable');
      const j=await response.json();
      const loaded=[];j.categories.forEach(c=>c.products.forEach(p=>loaded.push(p)));
      items=loaded;return items;
    })().finally(()=>{loading=null;});
    return loading;
  }
  async function run(revision){
    if(revision!==searchRevision)return;
    const q=sInput.value.trim().toLowerCase();
    if(!q){results.hidden=true;results.innerHTML='';if(catGrid)catGrid.style.display='';countEl.textContent='';return;}
    let catalog;
    try{catalog=await load();}
    catch{
      if(revision!==searchRevision)return;
      results.hidden=true;results.innerHTML='';if(catGrid)catGrid.style.display='';
      countEl.textContent='Search is temporarily unavailable. Please browse the categories or try again.';
      return;
    }
    // Typing or clearing invalidates old results immediately, before the debounce.
    if(revision!==searchRevision)return;
    const list=catalog.filter(p=>{
      // A shorthand group such as RW337/285 must also be found as RW285.
      const prefix=(p.sku.match(/^[a-z]+/i)||[''])[0];
      const codes=p.sku.split('/').map(code=>/^\d+$/.test(code)?prefix+code:code).join(' ');
      return (p.sku+' '+codes+' '+p.title+' '+p.category).toLowerCase().indexOf(q)>-1;
    }).sort((a,b)=>Number(b.sku.toLowerCase()===q)-Number(a.sku.toLowerCase()===q));
    matches=list;shown=0;results.innerHTML='';
    show(paging?24:matches.length);
    results.hidden=false;if(catGrid)catGrid.style.display='none';
  }
  sInput.addEventListener('input',()=>{
    clearTimeout(tmr);
    matches=[];shown=0;if(paging)paging.hidden=true;
    const revision=++searchRevision;
    if(!sInput.value.trim())run(revision);
    else tmr=setTimeout(()=>run(revision),160);
  });
  const pre=new URLSearchParams(location.search).get('search');
  if(pre){sInput.value=pre;run(++searchRevision);}
})();

// 询盘篮 Quote Basket(localStorage,多SKU一次询价)
(function(){
  const KEY='qcBasket';
  const load=()=>{
    try{
      const stored=JSON.parse(localStorage.getItem(KEY)||'[]');
      if(!Array.isArray(stored))return[];
      const seen=new Set();
      return stored.filter(item=>{
        if(!item||typeof item.sku!=='string'||!item.sku.trim()||seen.has(item.sku))return false;
        seen.add(item.sku);return true;
      }).map(item=>({sku:item.sku,image:typeof item.image==='string'?item.image:''}));
    }catch(e){return[];}
  };
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
  function safeLocalImage(src){
    const value=String(src||'').trim();
    if(!value)return '';
    try{
      const url=new URL(value,location.origin);
      if(url.origin!==location.origin||!url.pathname.startsWith('/assets/'))return '';
      return url.pathname+url.search;
    }catch(e){return '';}
  }
  function imageFromButton(a){
    const scopes=[a.closest('.product-card'),a.closest('.detail-grid'),a.closest('.product-info'),document];
    let src=safeLocalImage(a.dataset.image||new URLSearchParams(location.search).get('image')||'');
    for(const scope of scopes){
      if(src||!scope)continue;
      const img=scope.querySelector('.product-img img,.gallery-main img,img');
      src=safeLocalImage(img&&img.getAttribute('src')||'');
    }
    return src;
  }
  let catalogImages=null;
  async function loadCatalogImages(){
    if(catalogImages)return catalogImages;
    catalogImages={};
    try{
      const j=await (await fetch('assets/data/product-catalog.json?v=20261018-extension')).json();
      (j.categories||[]).forEach(c=>(c.products||[]).forEach(p=>{if(p.sku&&!catalogImages[p.sku])catalogImages[p.sku]=safeLocalImage(p.image||'');}));
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
    a.classList.add('added');a.textContent='✓ In list';a.setAttribute('aria-pressed','true');
    renderChip();
  });
  // 已在篮中的按钮标记
  document.querySelectorAll('.basket-add').forEach(a=>{
    a.setAttribute('aria-pressed',String(load().some(x=>x.sku===a.dataset.sku)));
    if(load().some(x=>x.sku===a.dataset.sku)){a.classList.add('added');a.textContent='✓ In list';}
  });
  // quote 页:渲染篮面板 + 预填 textarea
  if(/quote\.html$/.test(location.pathname)){
    const form=document.querySelector('.quote-form-v2, .quote-form');
    const ta=form?form.querySelector('textarea[name="message"], textarea'):null;
    let previousSkus=[];
    function syncTa(){
      const list=normalizeList(load());
      if(!ta)return;
      const known=previousSkus.slice().sort((a,b)=>b.length-a.length);
      const edited=new Map();
      let rest=ta.value;
      const old=rest.match(/^Inquiry list:\r?\n((?:- [^\r\n]*(?:\r?\n|$))*)(?:\r?\n)?/);
      if(old){
        const notes=[];
        old[1].split(/\r?\n/).filter(Boolean).forEach(line=>{
          const sku=known.find(s=>line==='- '+s||line.startsWith('- '+s+' ')||line.startsWith('- '+s+':')||line.startsWith('- '+s+'\t'));
          if(sku)edited.set(sku,line);else notes.push(line);
        });
        // Only manage recognized SKU lines. A buyer's similarly named list is their own text.
        if(edited.size)rest=(notes.length?notes.join('\n')+'\n\n':'')+rest.slice(old[0].length);
      }
      const block=list.length?('Inquiry list:\n'+list.map(x=>edited.get(x.sku)||'- '+x.sku).join('\n')+'\n\n'):'';
      previousSkus=list.map(x=>x.sku);
      if(ta.value!==block+rest){
        ta.value=block+rest;
      }
      // Selections can change even when the buyer has replaced the generated text.
      ta.dispatchEvent(new Event('input',{bubbles:true}));
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
      p.innerHTML='<h3>Your inquiry list ('+list.length+') <button type="button" class="bp-clear" data-clear aria-label="Clear inquiry list">clear all</button></h3><ul>'+
        list.map(x=>'<li><span class="bp-item"><img src="'+esc(safeLocalImage(x.image)||'/assets/images/favicon.png')+'" alt="'+esc(x.sku)+'" loading="lazy"><b>'+esc(x.sku)+'</b></span><button type="button" class="bp-remove" data-sku="'+esc(x.sku)+'" aria-label="Remove '+esc(x.sku)+' from inquiry list">×</button></li>').join('')+'</ul>';
      syncTa();renderChip();
    }
    document.addEventListener('click',async e=>{
      const remove=e.target.closest('.bp-remove');
      const clear=e.target.closest('.bp-clear');
      if(!remove&&!clear)return;
      const buttons=[...document.querySelectorAll('.bp-remove')];
      const index=remove?buttons.indexOf(remove):0;
      save(remove?load().filter(x=>x.sku!==remove.dataset.sku):[]);
      await renderPanel();
      const remaining=document.querySelectorAll('.bp-remove');
      (remaining[Math.min(index,remaining.length-1)]||ta)?.focus();
    });
    renderPanel();
    // Keep saved selections until the buyer explicitly removes or clears them.
    // A native third-party POST does not provide a verified delivery receipt here.
  }
})();
