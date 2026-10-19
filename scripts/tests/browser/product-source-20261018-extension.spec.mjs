import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
const manifest=JSON.parse(readFileSync('docs/product-batch-manifest-20261018-extension.json','utf8'));
const all=JSON.parse(readFileSync('assets/data/product-catalog.json','utf8')).categories.flatMap(c=>c.products);
const categories={'resin-charms':'Resin Charms','polymer-clay-slices':'Polymer Clay Sprinkles','plastic-sequins':'Glitter & Fillers','plastic-beads':'Acrylic Beads','pvc-plastic-charms':'Other','jewelry-accessories':'Jewelry Accessories'};
test('extension SKUs connect galleries, exact searches and quote context',async({page})=>{
 await page.route('**/formsubmit.co/**',r=>r.abort());await page.route('**/api/inquiry',r=>r.abort());
 for(const record of manifest.products){
  const p=all.find(p=>p.sku===record.sku);await page.goto(p.pdp,{waitUntil:'domcontentloaded'});
  await expect(page.locator('h1')).toHaveText(p.title);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  const images=page.locator('.gallery-main img,.gallery-row img');await expect(images).toHaveCount(3);
  for(let i=0;i<3;i++){await images.nth(i).scrollIntoViewIfNeeded();await expect.poll(()=>images.nth(i).evaluate(i=>i.complete&&i.naturalWidth>0)).toBe(true);}
  if(['YZ26165','RW0024009'].includes(p.sku))await page.screenshot({path:`test-results/extension-${p.sku}-${test.info().project.name}.png`,fullPage:true});
  await page.locator('.detail-grid a.btn-primary').click();
  await expect(page.locator('[name="selected_sku"]')).toHaveValue(p.sku);
  await expect(page.locator('#pPreviewTitle')).toHaveText(p.sku+' '+p.title);
  await expect(page.locator('select[name="product"]')).toHaveValue(categories[p.categorySlug]);
  await page.goto('products.html?search='+p.sku);
  await expect(page.locator('[data-search-results] .product-card .basket-add').first()).toHaveAttribute('data-sku',p.sku);
 }
 expect(all.length).toBeGreaterThanOrEqual(manifest.catalogCountAfter);
});
