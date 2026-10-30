import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

const catalog=JSON.parse(readFileSync(new URL('../../../assets/data/product-catalog.json',import.meta.url),'utf8'));
const matches=catalog.categories.flatMap(c=>c.products).filter(p=>(p.sku+' '+p.title+' '+p.category).toLowerCase().includes('resin'));

test('broad catalog searches reach every result, retain inquiry context and clear cleanly',async({page,context,baseURL})=>{
 await context.route('**/*',route=>new URL(route.request().url()).origin===new URL(baseURL).origin&&route.request().method()==='GET'?route.continue():route.abort());
 await page.emulateMedia({reducedMotion:'reduce'});
 await page.goto('/products.html?search=resin');
 const cards=page.locator('[data-search-results] .product-card');
 await expect(cards).toHaveCount(24);
 await expect(page.locator('[data-search-count]')).toContainText(`24 of ${matches.length}`);
 await page.locator('[data-search-more]').press('Enter');
 await expect(cards).toHaveCount(48);
 await page.locator('[data-search-all]').press('Enter');
 await expect(cards).toHaveCount(matches.length);
 const actual=await cards.locator('.basket-add').evaluateAll(nodes=>nodes.map(n=>n.dataset.sku));
 expect(actual).toEqual(matches.map(p=>p.sku));
 const last=matches.at(-1);
 await expect(cards.last().locator('h3 a')).toHaveAttribute('href',last.pdp);
 await cards.last().locator('.basket-add').press('Enter');
 await expect.poll(()=>page.evaluate(()=>JSON.parse(localStorage.getItem('qcBasket')||'[]').map(p=>p.sku))).toEqual([last.sku]);
 await page.locator('[data-catalog-search]').fill(last.sku);
 await expect(cards.first().locator('.basket-add')).toHaveAttribute('data-sku',last.sku);
 await page.locator('[data-catalog-search]').fill('');
 await expect(page.locator('[data-search-results]')).toBeHidden();
 await expect(page.locator('[data-search-controls]')).toBeHidden();
 await expect(page.locator('.category-grid')).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
});
