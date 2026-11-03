import { test, expect } from '@playwright/test';

test.beforeEach(async ({ context, baseURL }) => {
  const origin = new URL(baseURL).origin;
  await context.route('**/*', route => {
    if (new URL(route.request().url()).origin !== origin || route.request().method() !== 'GET') return route.abort();
    return route.continue();
  });
});

test('new inquiry links keep product context without another query document', async ({ page }) => {
  await page.goto('p-czb26337.html');
  const cta = page.locator('.pdp-cta .btn-primary');
  const url = new URL(await cta.getAttribute('href'), page.url());
  expect(url.search).toBe('');
  expect(url.hash).toMatch(/^#rfq:/);
  await cta.click();
  await expect(page.locator('#hiddenSku')).toHaveValue('CZB26337');
  await expect(page.locator('select[name="product"]')).toHaveValue('Resin Charms');
  await expect(page.locator('#pPreviewTitle')).toContainText('Cute Pig');
  await expect(page.locator('#pPreviewImg')).toHaveAttribute('src', /\/assets\/images\/pdp\/czb26337\//);
  await expect(page.locator('#hiddenUrl')).toHaveValue('https://www.qulacrafts.com/p-czb26337.html');
  await expect(page.locator('textarea[name="message"]')).toHaveValue(/Cute Pig/);
});

test('old query links and query priority remain supported', async ({ page }) => {
  await page.goto('quote.html?sku=YX625&product=Red%20Heart&category=Polymer%20Clay%20Sprinkles#rfq:sku=IGNORED&product=Ignored');
  await expect(page.locator('#hiddenSku')).toHaveValue('YX625');
  await expect(page.locator('#pPreviewTitle')).toHaveText('Red Heart');
  await expect(page.locator('select[name="product"]')).toHaveValue('Polymer Clay Sprinkles');
  await expect(page.locator('#qula-analytics-consent')).toBeHidden();
});

test('application selection survives fragment form state', async ({ page }) => {
  await page.goto('quote.html#rfq:application=Nail%20Art&source=homepage-buyer-feedback');
  await expect(page.locator('[name="application"]')).toHaveValue('Nail Art');
  await expect(page.locator('button[type="submit"]')).toBeEnabled();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
});
