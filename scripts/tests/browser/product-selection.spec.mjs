import { test, expect } from '@playwright/test';

// Exercise the added buyer path and the original primary CTA independently.
// Do not submit forms, open contact applications or emit analytics during QA.
test.beforeEach(async ({ page }) => {
  await page.route(/formsubmit\.co|google-analytics\.com|googletagmanager\.com|clarity\.ms/, route => route.abort());
  await page.route('**/api/inquiry', route => route.abort());
});

for (const sku of ['YX043', 'YX3194', 'YX3301', 'YA425', 'YA382', 'CZB26353', 'YX3531', 'CZB25840']) {
  test(`${sku}: project checks keep the correct product in the inquiry`, async ({ page }) => {
    await page.goto(`p-${sku.toLowerCase()}.html`, { waitUntil: 'domcontentloaded' });
    const original = page.locator('.pdp-cta a.btn-primary');
    const originalHref = await original.getAttribute('href');
    await expect(page.locator('.detail-grid a.btn-primary')).toHaveCount(1);
    await page.locator('[data-selection-jump] a').click();
    const section = page.locator(`[data-product-selection="${sku}"]`);
    await expect(section).toBeInViewport();
    await expect(section.locator('li')).toHaveCount(3);
    for (const link of await section.locator('a:not([data-selection-inquiry])').all()) {
      const href = await link.getAttribute('href');
      const response = await page.request.get(href);
      expect(response.status()).toBe(200);
    }
    const action = section.locator('[data-selection-inquiry]');
    expect(await action.getAttribute('href')).toBe(originalHref);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
    await action.click();
    await expect(page.locator('[name="selected_sku"]')).toHaveValue(sku);
    const category = sku.startsWith('YX') ? 'Polymer Clay Sprinkles' : sku.startsWith('YA') ? 'Acrylic Beads' : 'Beads for Pens';
    await expect(page.locator('select[name="product"]')).toHaveValue(category);
    const destination = new URL(page.url());
    const image = destination.searchParams.get('image');
    await expect(page.locator('#pPreviewTitle')).toHaveText(destination.searchParams.get('product'));
    const normalizedImage = new URL(image, page.url());
    await expect(page.locator('#pPreviewImg')).toHaveAttribute('src', normalizedImage.pathname + normalizedImage.search);
    await page.locator('[name="quantity"]').fill('500 pieces; sample fit review requested');
    await page.locator('[name="message"]').fill(`Please review the sample and packing for ${sku}.`);
    const whatsapp = await page.locator('#inquiryForm [data-inquiry-whatsapp]').getAttribute('href');
    const contactText = new URL(whatsapp).searchParams.get('text');
    expect(contactText).toContain(sku);
    expect(contactText).toContain('500 pieces; sample fit review requested');
    expect(contactText).toContain(`Please review the sample and packing for ${sku}.`);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
  });
}
