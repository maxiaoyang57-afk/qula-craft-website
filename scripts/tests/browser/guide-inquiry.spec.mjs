import { test, expect } from '@playwright/test';

// Two catalog references share YM109: check the image, title and reference URL,
// rather than accepting a correct SKU alone. Never send a form or analytics hit.
test.beforeEach(async ({ page }) => {
  await page.route(/formsubmit\.co|google-analytics\.com|googletagmanager\.com|clarity\.ms/, route => route.abort());
  await page.route('**/api/inquiry', route => route.abort());
});

const cases = [
  ['guide-slime-business-supply-checklist.html', 'p-yx043.html', 'YX043', 'assets/images/pdp/yx043/01.webp', 'Polymer Clay Sprinkles'],
  ['guide-slime-business-supply-checklist.html', 'p-yx3194.html', 'YX3194', 'assets/images/pdp/yx3194/yx3194-1-rainbow-cloud-polymer-clay-sprinkles.jpg', 'Polymer Clay Sprinkles'],
  ['guide-slime-business-supply-checklist.html', 'p-ym109.html', 'YM109', 'assets/images/pdp/ym109/01.webp', 'Glitter & Fillers'],
  ['guide-bingsu-beads-slime-fillers.html', 'p-ym109.html', 'YM109', 'assets/images/pdp/ym109/01.webp', 'Glitter & Fillers'],
  ['guide-bingsu-beads-slime-fillers.html', 'p-ym109-2.html', 'YM109', 'assets/images/pdp/ym109-2/01.webp', 'Glitter & Fillers'],
];

for (const [guide, pdp, sku, image, category] of cases) {
  test(`${guide} carries the exact ${pdp} reference into an inquiry`, async ({ page }) => {
    await page.goto(guide, { waitUntil: 'domcontentloaded' });
    const action = page.locator(`[data-guide-product-inquiry="${pdp}"]`);
    await expect(action).toBeVisible();
    const destination = new URL(await action.getAttribute('href'), page.url());
    expect(destination.searchParams.get('sku')).toBe(sku);
    expect(destination.searchParams.get('image')).toBe(image);
    await action.click();
    await expect(page.locator('#hiddenSku')).toHaveValue(sku);
    await expect(page.locator('#pPreviewImg')).toHaveAttribute('src', '/' + image);
    await expect(page.locator('#pPreviewTitle')).toHaveText(destination.searchParams.get('product'));
    await expect(page.locator('select[name="product"]')).toHaveValue(category);
    await expect(page.locator('[name="entry_page"]')).toHaveValue('https://www.qulacrafts.com/' + guide);
    await expect(page.locator('#hiddenUrl')).toHaveValue('https://www.qulacrafts.com/' + guide);
    await expect(page.locator('[name="application"]')).toHaveValue('Slime add-in selection; catalog reference: https://www.qulacrafts.com/' + pdp);
    const contactText = new URL(await page.locator('#inquiryForm [data-inquiry-whatsapp]').getAttribute('href')).searchParams.get('text');
    expect(contactText).toContain('https://www.qulacrafts.com/' + pdp);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
  });
}
