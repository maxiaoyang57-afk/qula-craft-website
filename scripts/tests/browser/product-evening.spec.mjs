import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
const manifest=JSON.parse(readFileSync('docs/product-batch-manifest-20261016-evening.json','utf8'));
const catalog=JSON.parse(readFileSync('assets/data/product-catalog.json','utf8'));
const all=catalog.categories.flatMap(c=>c.products);
test('evening product discovery, galleries and complete SKU inquiries',async({page})=>{
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
  if(['RW003270','RW337/285','YQ029','CDK0020110-7/CDK0020110-6/CDK0020110-5/CDK0020110'].includes(p.sku)) {
   await page.screenshot({path:`test-results/evening-${record.pdp.replace('.html','')}-${test.info().project.name}.png`,fullPage:true});
  }
  await page.locator('.detail-grid a.btn-primary').click();
  await expect(page.locator('[name="selected_sku"]')).toHaveValue(p.sku);
  await expect(page.locator('#pPreviewTitle')).toHaveText(p.sku+' '+p.title);
  expect(await page.locator('#message').inputValue()).toContain(p.sku);
  await expect(page.locator('select[name="product"]')).toHaveValue(new URL(p.inquiryUrl,'https://www.qulacrafts.com').searchParams.get('category'));
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
 }
 const group=all.find(p=>p.sku==='RW337/285');
 for(const query of ['RW285','rw285','RW337','RW337/285']) {
  await page.goto('products.html?search='+encodeURIComponent(query));
  await expect(page.locator('.product-card .basket-add[data-sku="RW337/285"]').first()).toBeVisible();
 }
 await page.goto('products.html?search='+encodeURIComponent(group.sku));
 await expect(page.locator('.product-card .basket-add[data-sku="RW337/285"]').first()).toBeVisible();
 await page.locator('.product-card .basket-add[data-sku="RW337/285"]').first().click();
 expect(await page.evaluate(()=>JSON.stringify(JSON.parse(localStorage.getItem('qcBasket')||'[]')))).toContain('RW337/285');
});
