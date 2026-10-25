import { test, expect } from '@playwright/test';

test.beforeEach(async({page})=>{
  await page.route('**/formsubmit.co/**',route=>route.abort());
  await page.route('**/api/inquiry',route=>route.abort());
});
test('polymer guide connects each curated motif to its exact product page',async({page})=>{
  await page.goto('guide-polymer-clay-sprinkles-bulk.html');
  const shortlist=page.locator('#polymer-design-shortlist');
  await expect(shortlist.locator('.product-card')).toHaveCount(3);
  for(const sku of ['YX043','YX3194','YX3301']) await expect(shortlist.locator('[data-sku="'+sku+'"]').first()).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  await shortlist.getByRole('link',{name:/YX3301.*Monkey/}).first().click();
  await expect(page).toHaveURL(/p-yx3301\.html/);
  await expect(page.locator('h1')).toHaveText('Monkey and Banana Polymer Clay Sprinkles');
});
test('multi-design checklist reaches the existing custom inquiry and preserves the brief in direct contact',async({page})=>{
  await page.goto('customization.html');
  await expect(page.locator('#multi-design-brief')).toContainText('bulk quantity for each design');
  await page.getByRole('link',{name:'Discuss a multi-design collection',exact:true}).click();
  const form=page.locator('#custom-project-inquiry');
  await expect(form).toBeVisible();
  await form.locator('[name="message"]').fill('Design A: matte resin; sample 1; bulk 100. Design B: glossy resin; sample 1; bulk 250.');
  const link=await form.locator('[data-inquiry-whatsapp]').getAttribute('href');
  expect(new URL(link).searchParams.get('text')).toContain('Design B: glossy resin');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
});
