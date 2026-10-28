import { test, expect } from 'playwright/test';
import { readFileSync } from 'node:fs';
const manifest = JSON.parse(readFileSync('docs/product-batch-manifest-20261028-monica-15.json', 'utf8'));
const products = JSON.parse(readFileSync('assets/data/product-catalog.json', 'utf8')).categories.flatMap(c => c.products);

test('Fifteenth Monica batch keeps all three images, exact SKU search and inquiry selection', async ({ page }) => {
  await page.route('**/formsubmit.co/**', route => route.abort());
  await page.route('**/api/inquiry', route => route.abort());
  await page.route('https://**/*', route => route.abort());
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  for (const record of manifest.products) {
    const product = products.find(p => p.sku === record.sku);
    await page.goto(product.pdp, { waitUntil: 'domcontentloaded' });
    await expect(page.locator('h1')).toHaveText(product.title);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
    const images = page.locator('.gallery-main img,.gallery-row img');
    await expect(images).toHaveCount(3);
    for (let i = 0; i < 3; i++) {
      await expect(images.nth(i)).toHaveAttribute('src', record.imageOutputs[i].path);
      await images.nth(i).scrollIntoViewIfNeeded();
      await expect.poll(() => images.nth(i).evaluate(image => image.complete && image.naturalWidth > 0)).toBe(true);
    }
    await page.locator('.detail-grid a.btn-primary').click();
    await expect(page.locator('[name="selected_sku"]')).toHaveValue(product.sku);
    await expect(page.locator('#pPreviewTitle')).toHaveText(product.sku + ' ' + product.title);
    await expect(page.locator('select[name="product"]')).toHaveValue('Resin Charms');
    const selectedImage = page.locator('#selectedProduct img');
    await expect.poll(async () => new URL(await selectedImage.getAttribute('src'), page.url()).pathname).toBe('/' + product.image);
    await page.goto('products.html?search=' + encodeURIComponent(product.sku));
    await expect(page.locator('[data-search-results] .product-card .basket-add').first()).toHaveAttribute('data-sku', product.sku);
  }
  expect(errors).toEqual([]);
});
