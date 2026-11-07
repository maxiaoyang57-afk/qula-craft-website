import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
const guides=JSON.parse(readFileSync('assets/data/product-selection-guides.json','utf8'));
const cases=[['ya855','YA855','Acrylic Beads','Approx. 2 mm'],['rw22372','RW22372','Resin Charms','21 mm'],['slm10094','SLM10094','Slime Charms','30 g'],['slm10093','SLM10093','Slime Charms','500 g'],['slm10012','SLM10012','Slime Charms','500 g'],['cdk001208','CDK001208','Keychains','Bag and keychain decoration']];
for(const [key,sku,category,fact]of cases)test(`${sku} keeps facts and project brief through inquiry`,async({page,context})=>{
 await context.route(/formsubmit\.co|google-analytics\.com|googletagmanager\.com|clarity\.ms|\/api\/inquiry/,r=>r.abort());
 await page.emulateMedia({reducedMotion:'reduce'});await page.goto('/p-'+key+'.html',{waitUntil:'domcontentloaded'});
 await expect(page.locator('.spec-table')).toContainText(fact);
 const section=page.locator('[data-product-selection="'+sku+'"]');await expect(section).toHaveCount(1);
 const cta=section.locator('[data-selection-inquiry]');await cta.scrollIntoViewIfNeeded();await cta.press('Enter');
 await expect(page.locator('#hiddenSku')).toHaveValue(sku);await expect(page.locator('select[name="product"]')).toHaveValue(category);
 await expect(page.locator('[name="application"]')).toHaveValue(guides[key].inquiryBrief);
 const selectedName=await page.locator('#pPreviewTitle').innerText();
 expect(await page.locator('#inquiryForm [name="message"]').inputValue()).toContain(selectedName);
 const contactDraft=new URL(await page.locator('#inquiryForm [data-inquiry-whatsapp]').getAttribute('href')).searchParams.get('text');
 expect(contactDraft).toContain(sku);expect(contactDraft).toContain(guides[key].inquiryBrief);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
});
