import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
const manifest=JSON.parse(readFileSync('docs/product-batch-manifest-20261018.json','utf8'));
const all=JSON.parse(readFileSync('assets/data/product-catalog.json','utf8')).categories.flatMap(c=>c.products);
test('October 18 galleries, search and exact inquiry selections work',async({page})=>{
 await page.route('**/formsubmit.co/**',r=>r.abort());
 await page.route('**/api/inquiry',r=>r.abort());
 for(const record of manifest.products){
  const p=all.find(p=>p.sku===record.sku);
  await page.goto(p.pdp,{waitUntil:'domcontentloaded'});
  await expect(page.locator('h1')).toHaveText(p.title);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  const images=page.locator('.gallery-main img,.gallery-row img');await expect(images).toHaveCount(3);
  for(let i=0;i<3;i++){await images.nth(i).scrollIntoViewIfNeeded();await expect.poll(()=>images.nth(i).evaluate(i=>i.complete&&i.naturalWidth>0)).toBe(true);}
  if(['RW26808','RW26804'].includes(p.sku))await page.screenshot({path:`test-results/oct18-${p.sku}-${test.info().project.name}.png`,fullPage:true});
  await page.locator('.detail-grid a.btn-primary').click();
  await expect(page.locator('[name="selected_sku"]')).toHaveValue(p.sku);
  await expect(page.locator('#pPreviewTitle')).toHaveText(p.sku+' '+p.title);
  await expect(page.locator('select[name="product"]')).toHaveValue('Resin Charms');
  expect(await page.locator('#message').inputValue()).toContain(p.sku);
  await page.goto('products.html?search='+p.sku);
  await expect(page.locator('.product-card .basket-add[data-sku="'+p.sku+'"]').first()).toBeVisible();
 }
 for(const sku of ['RW26800','RW26796','RW20809'])expect(all.filter(p=>p.sku===sku)).toHaveLength(1);
 expect(all.find(p=>p.sku==='RW26808').pdp).toBe('p-rw26808-acorn.html');
});
