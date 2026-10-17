import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
const manifest=JSON.parse(readFileSync('docs/product-batch-manifest-20261017.json','utf8'));
const all=JSON.parse(readFileSync('assets/data/product-catalog.json','utf8')).categories.flatMap(c=>c.products);
test('October 17 source batch retains galleries, mixed SKUs and quote selections',async({page})=>{
 await page.route('**/formsubmit.co/**',r=>r.abort());
 await page.route('**/api/inquiry',r=>r.abort());
 for(const record of manifest.products){
  const p=all.find(p=>p.sku===record.sku);
  await page.goto(p.pdp,{waitUntil:'domcontentloaded'});
  await expect(page.locator('h1')).toHaveText(p.title);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  const images=page.locator('.gallery-main img,.gallery-row img');
  await expect(images).toHaveCount(3);
  for(let i=0;i<3;i++){await images.nth(i).scrollIntoViewIfNeeded();await expect.poll(()=>images.nth(i).evaluate(i=>i.complete&&i.naturalWidth>0)).toBe(true);}
  if(['ABC041-ABC042','RW26811','RW21765'].includes(p.sku)||p.sku.startsWith('CDK938-6/'))await page.screenshot({path:`test-results/source-${record.pdp.replace('.html','')}-${test.info().project.name}.png`,fullPage:true});
  await page.locator('.detail-grid a.btn-primary').click();
  await expect(page.locator('[name="selected_sku"]')).toHaveValue(p.sku);
  await expect(page.locator('#pPreviewTitle')).toHaveText(p.sku+' '+p.title);
  expect(await page.locator('#message').inputValue()).toContain(p.sku);
  await expect(page.locator('select[name="product"]')).toHaveValue(new URL(p.inquiryUrl,'https://www.qulacrafts.com').searchParams.get('category'));
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
 }
 for(const sku of ['CDK938-6/CDK003939-2/CDK938-5/CDK938-4','CDK938-9/CDK159-1/CDK938-7','ABC041-ABC042','RW26811']){
  await page.goto('products.html?search='+encodeURIComponent(sku));
  await expect(page.locator('.product-card .basket-add[data-sku="'+sku+'"]').first()).toBeVisible();
 }
});
