import { test, expect } from '@playwright/test';

test('resin cards show confirmed dimensions and packing before the inquiry link', async ({ page }) => {
  await page.goto('/resin-charms.html');
  const card = sku => page.locator('.product-card').filter({ has: page.locator('[data-sku="' + sku + '"]') });
  await expect(card('RW26883').locator('.card-specs')).toHaveText('13 × 15 mm · 100 pcs/bag');
  await expect(card('RW26746').locator('.card-specs')).toHaveText('47 × 47 mm · 10 sets/bag');
  await expect(card('RW23792').locator('.card-specs')).toHaveText('about 26 × 28 mm');
  await expect(card('RW1959').locator('.card-specs')).toHaveText('100 pcs/bag');
  await expect(card('RW24466').locator('.card-specs')).toHaveCount(0);
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
