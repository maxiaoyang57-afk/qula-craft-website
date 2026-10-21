import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

const catalog = JSON.parse(readFileSync(new URL('../../../assets/data/product-catalog.json', import.meta.url), 'utf8'));
const firstSku = 'RW26808', secondSku = 'RW20809';
const catalogPath = '/assets/data/product-catalog.json';

test('clearing a search during a delayed catalog download does not bring the old results back', async ({ page, context, baseURL }) => {
  const origin = new URL(baseURL).origin, errors = [], sends = [];
  let release;
  const gate = new Promise(resolve => { release = resolve; });
  let downloads = 0;
  page.on('pageerror', error => errors.push(error.message));
  await context.route('**/*', async route => {
    const request = route.request(), url = new URL(request.url());
    if (request.method() !== 'GET') { sends.push(request.url()); return route.abort(); }
    if (url.origin !== origin) return route.abort();
    if (url.pathname === catalogPath) {
      downloads++;
      await gate;
      return route.fulfill({ json: catalog });
    }
    return route.continue();
  });
  try {
    await page.goto('products.html');
    await page.locator('[data-catalog-search]').fill(firstSku);
    await expect.poll(() => downloads).toBe(1);
    await page.locator('[data-catalog-search]').fill('');
    await expect(page.locator('.category-grid')).toBeVisible();
    const response = page.waitForResponse(response => new URL(response.url()).pathname === catalogPath);
    release();
    await (await response).finished();
    // Allow the downloaded JSON and its result-rendering microtasks to complete.
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    await expect(page.locator('[data-search-results]')).toBeHidden();
    await expect(page.locator('[data-search-results]')).toBeEmpty();
    await expect(page.locator('[data-search-count]')).toHaveText('');
    await expect(page.locator('.category-grid')).toBeVisible();
    await page.locator('[data-catalog-search]').fill(secondSku);
    await expect(page.locator('[data-search-results] .basket-add').first()).toHaveAttribute('data-sku', secondSku);
    expect(downloads).toBe(1);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
    expect(errors).toEqual([]);
    expect(sends).toEqual([]);
  } finally { release(); }
});

test('a failed search preserves category navigation and can recover on the next query', async ({ page, context, baseURL }) => {
  const origin = new URL(baseURL).origin, errors = [], sends = [];
  let downloads = 0;
  page.on('pageerror', error => errors.push(error.message));
  await context.route('**/*', async route => {
    const request = route.request(), url = new URL(request.url());
    if (request.method() !== 'GET') { sends.push(request.url()); return route.abort(); }
    if (url.origin !== origin) return route.abort();
    if (url.pathname === catalogPath) {
      downloads++;
      return downloads === 1
        ? route.fulfill({ status: 503, json: { error: 'Synthetic unavailable catalog' } })
        : route.fulfill({ json: catalog });
    }
    return route.continue();
  });
  await page.goto('products.html');
  await page.locator('[data-catalog-search]').fill(firstSku);
  await expect(page.locator('[data-search-count]')).toContainText('temporarily unavailable');
  await expect(page.locator('.category-grid a[href="resin-charms.html"]')).toBeVisible();
  await expect(page.locator('[data-search-results]')).toBeHidden();
  await page.locator('[data-catalog-search]').fill(secondSku);
  await expect(page.locator('[data-search-results] .basket-add').first()).toHaveAttribute('data-sku', secondSku);
  await expect(page.locator('[data-search-count]')).toContainText('matching item');
  expect(downloads).toBe(2);
  expect(errors).toEqual([]);
  expect(sends).toEqual([]);
});
