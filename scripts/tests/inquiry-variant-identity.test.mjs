import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const main=fs.readFileSync(new URL('../../assets/js/main.js',import.meta.url),'utf8');
const source=main.slice(main.indexOf('// 询盘篮 Quote Basket'));
function harness(path='/products.html',initial=[]){
  let stored=JSON.stringify(initial),panel=null;
  const listeners=[];
  const classes=()=>{const set=new Set();return{contains:x=>set.has(x),add:x=>set.add(x),toggle:(x,on)=>on?set.add(x):set.delete(x)}};
  const counter={textContent:''};
  const ta={value:'My custom packing requirements.',dispatchEvent(){},focus(){}};
  const element=()=>({classList:classes(),querySelector:s=>s==='b'?counter:null,remove(){panel=null},setAttribute(){},innerHTML:''});
  const form={querySelector:()=>ta,insertBefore(p){panel=p;}};
  const document={body:{appendChild(){}},createElement:element,querySelector:s=>s==='.quote-form-v2, .quote-form'?form:s==='.basket-panel'?panel:null,querySelectorAll:()=>[],addEventListener:(type,fn)=>{if(type==='click')listeners.push(fn)}};
  const products=[{sku:'YM109',pdp:'p-ym109.html',title:'First PET tube reference',category:'Plastic Sequins',image:'/assets/first.webp'},{sku:'YM109',pdp:'p-ym109-2.html',title:'Second PET tube reference',category:'Plastic Sequins',image:'/assets/second.webp'}];
  vm.runInNewContext(source,{URL,Event,document,location:{origin:'https://www.qulacrafts.com',pathname:path,search:''},localStorage:{getItem:()=>stored,setItem:(k,v)=>{stored=v}},fetch:async()=>({json:async()=>({categories:[{products}]})})});
  const button=p=>{const card={querySelector:s=>s==='a[href]'?{getAttribute:()=>p.pdp}:s==='h3'?{textContent:p.title}:null};return{dataset:{sku:p.sku,image:p.image},classList:classes(),closest:s=>s==='.product-card'?card:null,setAttribute(){},textContent:''}};
  const click=async(target)=>{for(const fn of listeners)await fn({target:{closest:s=>s==='.basket-add'&&target.add?target.add:s==='.bp-remove'&&target.remove?target.remove:s==='.bp-clear'&&target.clear?{}:null}})};
  return{products,button,click,items:()=>JSON.parse(stored),ta,panel:()=>panel,ready:()=>new Promise(resolve=>setImmediate(resolve))};
}
test('real delegated add handler retains both same-SKU products, deduplicates each URL and records full context',async()=>{
  const h=harness();const a=h.button(h.products[0]),b=h.button(h.products[1]);
  await h.click({add:a});await h.click({add:b});await h.click({add:h.button(h.products[0])});
  assert.equal(h.items().length,2);
  assert.deepEqual(h.items().map(x=>x.productPath),['/p-ym109.html','/p-ym109-2.html']);
  assert.deepEqual(h.items().map(x=>x.title),['First PET tube reference','Second PET tube reference']);
  assert.deepEqual(h.items().map(x=>x.image),['/assets/first.webp','/assets/second.webp']);
});
test('quote page enriches exact references and removes only the chosen variant',async()=>{
  const h=harness('/quote.html',[{sku:'YM109',productPath:'/p-ym109.html',image:'/assets/first.webp'},{sku:'YM109',productPath:'/p-ym109-2.html',image:'/assets/second.webp'}]);
  await h.ready();
  assert.equal(h.items().length,2);assert.ok(h.panel().innerHTML.includes('First PET tube reference')&&h.panel().innerHTML.includes('Second PET tube reference'));
  assert.ok(h.ta.value.includes('https://www.qulacrafts.com/p-ym109-2.html'));
  await h.click({remove:{dataset:{key:'/p-ym109.html'}}});
  assert.deepEqual(h.items().map(x=>x.productPath),['/p-ym109-2.html']);
  assert.ok(!h.ta.value.includes('First PET tube reference')&&h.ta.value.includes('Second PET tube reference'));
  await h.click({clear:true});assert.equal(h.ta.value,'My custom packing requirements.');
});
test('legacy ambiguous SKU-only selection is retained without silently choosing a version',async()=>{
  const h=harness('/quote.html',[{sku:'YM109',image:''}]);await h.ready();
  assert.equal(h.items()[0].productPath,undefined);
  assert.ok(h.panel().innerHTML.includes('confirm the exact product reference'));
});
