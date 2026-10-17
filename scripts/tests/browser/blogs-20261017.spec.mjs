import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
const articles=JSON.parse(readFileSync('scripts/data/blogs-20261017.json','utf8'));
test('new application articles keep product links, images and reading controls usable',async({page},info)=>{
 await page.route('**/formsubmit.co/**',r=>r.abort());
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/resources.html');
 for(const a of articles)await expect(page.locator('main a[href="'+a.slug+'"]')).toBeVisible();
 for(const a of articles){
  await page.goto('/'+a.slug);
  await expect(page.locator('h1')).toHaveText(a.title);
  const decline=page.locator('[data-analytics-decline]');if(await decline.isVisible())await decline.click();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  for(const img of await page.locator('main img').all()){
   await img.scrollIntoViewIfNeeded();
   await expect.poll(()=>img.evaluate(i=>i.complete&&i.naturalWidth>0)).toBe(true);
   expect(await img.evaluate(i=>Math.abs((i.getBoundingClientRect().width/i.getBoundingClientRect().height)-(i.naturalWidth/i.naturalHeight))<0.02)).toBe(true);
  }
  const links=await page.locator('main a[href]').evaluateAll(ls=>[...new Set(ls.map(l=>l.href).filter(h=>new URL(h).origin===location.origin))]);
  for(const link of links)expect((await page.request.get(link)).status(),link).toBe(200);
  await page.locator('main').screenshot({path:info.outputPath(a.slug.replace('.html','')+'.png')});
  await page.locator('main h2').last().scrollIntoViewIfNeeded();
  await page.locator('.back-top').click();
  await expect.poll(()=>page.evaluate(()=>scrollY)).toBeLessThan(5);
 }
 expect(errors).toEqual([]);
});
