import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
const entry=JSON.parse(readFileSync('assets/data/pdp-data.json','utf8')).find(p=>p.sku==='RW22372');
const product=JSON.parse(readFileSync('assets/data/product-catalog.json','utf8')).categories.flatMap(c=>c.products).find(p=>p.sku==='RW22372');
const brief=JSON.parse(readFileSync('assets/data/product-selection-guides.json','utf8')).rw22372.inquiryBrief;
test('RW22372 random mix keeps real images, packing, conditional MOQ and exact inquiry context',async({page,context})=>{
 await context.route(/formsubmit\.co|google-analytics\.com|googletagmanager\.com|clarity\.ms|\/api\/inquiry/,r=>r.abort());
 await page.emulateMedia({reducedMotion:'reduce'});
 const noOverflow=async()=>expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
 await page.goto('/resin-charms.html',{waitUntil:'domcontentloaded'});
 const card=page.locator('article.product-card').filter({has:page.locator('[data-sku="RW22372"]')});
 await expect(card).toHaveCount(1);await expect(card).toContainText('100 pieces/bag');await expect(card).toContainText('10 bags when not in stock');
 await expect(card.locator('img')).toHaveAttribute('src',entry.imagesLocal[0]);await noOverflow();
 // The full catalog progressively reveals cards. Use the visible curated
 // shortcut for this legacy SKU, then separately exercise exact-SKU search.
 await page.getByRole('link',{name:'RW22372 chocolate chip cookie flatback cabochons',exact:true}).press('Enter');
 await expect(page.locator('h1')).toHaveText(product.titleFull);
 const images=page.locator('.gallery-main img,.gallery-row img');await expect(images).toHaveCount(3);
 for(let i=0;i<3;i++){await expect(images.nth(i)).toHaveAttribute('src',entry.imagesLocal[i]);await images.nth(i).scrollIntoViewIfNeeded();await expect.poll(()=>images.nth(i).evaluate(e=>e.complete&&e.naturalWidth>0)).toBe(true);}
 await expect(page.locator('.spec-table')).toContainText('Random mixed designs and colors');
 await expect(page.locator('.spec-table')).toContainText('100 pieces per bag');
 await expect(page.locator('.spec-table')).toContainText('1 bag when in stock; 10 bags when not in stock');await noOverflow();
 const cta=page.locator('[data-selection-inquiry="RW22372"]');await cta.scrollIntoViewIfNeeded();await cta.press('Enter');
 await expect(page.locator('#hiddenSku')).toHaveValue('RW22372');await expect(page.locator('select[name="product"]')).toHaveValue('Resin Charms');
 await expect(page.locator('[name="application"]')).toHaveValue(brief);await expect(page.locator('#pPreviewTitle')).toHaveText(product.titleFull);
 await expect(page.locator('#pPreviewImg')).toHaveAttribute('src','/'+entry.imagesLocal[0]);
 expect(await page.locator('#inquiryForm [name="message"]').inputValue()).toContain(product.titleFull);
 const direct=page.locator('#inquiryForm [data-inquiry-whatsapp]');await expect(direct).toHaveAttribute('href',/[?&]text=/);
 const draft=new URL(await direct.getAttribute('href')).searchParams.get('text');expect(draft).toContain('RW22372');expect(draft).toContain(brief);await noOverflow();
 await page.goto('/products.html?search=RW22372');
 const result=page.locator('[data-search-results] .product-card').filter({has:page.locator('[data-sku="RW22372"]')});
 await expect(result).toHaveCount(1);await expect(result.locator('img')).toHaveAttribute('src',entry.imagesLocal[0]);await noOverflow();
});
