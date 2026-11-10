import { test, expect } from '@playwright/test';
const guide='guide-find-craft-supplies-from-photo.html';
test('reference-photo sourcing preserves each component through inquiry',async({page},testInfo)=>{
 await page.route(/formsubmit\.co|google-analytics\.com|googletagmanager\.com|clarity\.ms/,route=>route.abort());
 await page.route('**/api/inquiry',route=>route.abort());
 for(const [sku,category] of [['RW26801','Resin Charms'],['YX693','Polymer Clay Sprinkles'],['YX329','Polymer Clay Sprinkles'],['YA425','Acrylic Beads'],['CDK070','Keychains']]){
  await page.goto('/'+guide,{waitUntil:'domcontentloaded'});
  const action=page.locator(`[data-photo-product-inquiry="${sku}"]`);
  await action.scrollIntoViewIfNeeded();
  const image=action.locator('xpath=..').locator('img');
  await expect(image).toBeVisible();
  await expect.poll(()=>image.evaluate(el=>el.complete&&el.naturalWidth>0)).toBe(true);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  if(sku==='RW26801')await page.screenshot({path:testInfo.outputPath('photo-guide.png'),fullPage:true});
  const href=new URL(await action.getAttribute('href'),page.url());
  await action.click();
  await expect(page.locator('#hiddenSku')).toHaveValue(sku);
  await expect(page.locator('#pPreviewTitle')).toHaveText(href.searchParams.get('product'));
  await expect(page.locator('#pPreviewImg')).toHaveAttribute('src','/'+href.searchParams.get('image'));
  await expect(page.locator('select[name="product"]')).toHaveValue(category);
  await expect(page.locator('[name="entry_page"]')).toHaveValue('https://www.qulacrafts.com/'+guide);
 }
});
