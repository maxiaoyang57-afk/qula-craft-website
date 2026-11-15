import { test, expect } from '@playwright/test';
import { resinPageForSku } from './resin-catalog-pages.mjs';

test('resin cards show confirmed dimensions and packing before the inquiry link', async ({ page }) => {
  const card = sku => page.locator('.product-card').filter({ has: page.locator('[data-sku="' + sku + '"]') });
  for (const [sku, specs] of [
    ['RW26883', '13 × 15 mm · 100 pcs/bag'],
    ['RW26746', '47 × 47 mm · 10 sets/bag'],
    ['RW23792', 'about 26 × 28 mm'],
    ['RW1959', '100 pcs/bag'],
    ['RW24466', null],
  ]) {
    await page.goto(resinPageForSku(sku));
    const label = card(sku).locator('.card-specs');
    if (specs) await expect(label).toHaveText(specs);
    else await expect(label).toHaveCount(0);
  }
  await page.goto(resinPageForSku('RW26883'));
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
  // New arrivals can move this older SKU beyond the phone's initial 12 cards.
  // Reveal it through the buyer's normal paging control before asking about it.
  if (!(await card('RW26883').isVisible())) {
    await expect(card('RW26883')).toHaveAttribute('data-mobile-browse-hidden', '');
    // Each new batch can add another page before this protected older SKU.
    const more = page.locator('.mobile-browse-more:visible');
    const cardCount = await page.locator('.product-card').count();
    for (let pageNumber = 0; pageNumber < cardCount && !(await card('RW26883').isVisible()); pageNumber += 1) {
      await expect(more).toBeVisible();
      await more.click();
    }
    await expect(card('RW26883')).toBeVisible();
  }
  await card('RW26883').locator('a.btn-card').click();
  await expect(page.locator('#hiddenSku')).toHaveValue('RW26883');
});

test('resin catalog links reach the next page and keep buyer inquiry context', async ({ page, baseURL }) => {
  await page.route('**/*', route => {
    const request = route.request();
    return new URL(request.url()).origin === new URL(baseURL).origin && request.method() === 'GET'
      ? route.continue() : route.abort();
  });
  await page.goto('/resin-charms.html');
  await expect(page.locator('.product-card')).toHaveCount(48);
  const nav = page.getByRole('navigation', { name: 'Resin catalog pages' });
  await nav.getByRole('link', { name: 'Next', exact: true }).click();
  await expect(page).toHaveURL(/\/resin-charms-page-2\.html$/);
  await expect(nav.locator('[aria-current="page"]')).toHaveText('2');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
  const firstCard = page.locator('.product-card').first();
  const sku = await firstCard.locator('[data-sku]').first().getAttribute('data-sku');
  await firstCard.locator('h3 a').click();
  await expect(page).toHaveURL(/\/p-[^/]+\.html$/);
  const inquiry = page.locator('.detail-grid a.btn-primary').first();
  await inquiry.click();
  await expect(page.locator('#hiddenSku')).toHaveValue(sku);
});
