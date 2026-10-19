import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
const manifest=JSON.parse(readFileSync('docs/product-batch-manifest-20261019.json','utf8'));
const all=JSON.parse(readFileSync('assets/data/product-catalog.json','utf8')).categories.flatMap(c=>c.products);
const categories={'slime-charms':'Slime Charms','keychain':'Keychains','resin-charms':'Resin Charms','polymer-clay-slices':'Polymer Clay Sprinkles','plastic-sequins':'Glitter & Fillers','plastic-beads':'Acrylic Beads','pvc-plastic-charms':'Other','jewelry-accessories':'Jewelry Accessories'};
test('October 19 grouped SKUs connect galleries, exact searches and quote context',async({page})=>{
 await page.route('**/formsubmit.co/**',r=>r.abort());await page.route('**/api/inquiry',r=>r.abort());
 for(const record of manifest.products){
  const p=all.find(p=>p.sku===record.sku);await page.goto(p.pdp,{waitUntil:'domcontentloaded'});
  await page.evaluate(()=>document.fonts.ready);
  await expect(page.locator('h1')).toHaveText(p.title);
  const viewportWidth=page.viewportSize().width;
  const checkWidth=async()=>{
   const layout=await page.evaluate(()=>({width:document.documentElement.scrollWidth,overflow:[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.right>document.documentElement.clientWidth+1&&getComputedStyle(e).position!=='fixed'&&!e.closest('.gallery-row,.nav-dropdown')}).map(e=>({tag:e.tagName,cls:e.className,text:e.textContent.slice(0,80)})).slice(0,8)}));
   expect(layout.width,JSON.stringify(layout.overflow)).toBeLessThanOrEqual(viewportWidth+1);
  };
  await checkWidth();
  const images=page.locator('.gallery-main img,.gallery-row img');await expect(images).toHaveCount(record.imageOutputs.length);
  for(let i=0;i<record.imageOutputs.length;i++){await images.nth(i).scrollIntoViewIfNeeded();await expect.poll(()=>images.nth(i).evaluate(i=>i.complete&&i.naturalWidth>0)).toBe(true);}
  await page.evaluate(()=>window.scrollTo({top:0,left:0,behavior:'instant'}));
  await checkWidth();
  await page.screenshot({path:`test-results/oct19-${p.pdp}-${test.info().project.name}.png`,fullPage:true,animations:'disabled'});
  await page.locator('.detail-grid a.btn-primary').click();
  await expect(page.locator('[name="selected_sku"]')).toHaveValue(p.sku);
  await expect(page.locator('#pPreviewTitle')).toHaveText(p.sku+' '+p.title);
  await expect(page.locator('select[name="product"]')).toHaveValue(categories[p.categorySlug]);
  await page.goto('products.html?search='+encodeURIComponent(p.sku));
  await expect(page.locator('[data-search-results] .product-card .basket-add').first()).toHaveAttribute('data-sku',p.sku);
 }
 expect(all.length).toBeGreaterThanOrEqual(417);
});
