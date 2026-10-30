import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

const catalogText = readFileSync(new URL('../../../assets/data/product-catalog.json', import.meta.url), 'utf8');
const catalog = JSON.parse(catalogText);

test.beforeEach(async ({ context, baseURL }) => {
  const origin = new URL(baseURL).origin;
  await context.route('**/*', route => {
    const request = route.request();
    if (new URL(request.url()).origin !== origin || request.method() !== 'GET') return route.abort();
    return route.continue();
  });
});

test('quote categories follow catalog records rather than SKU prefixes', async ({ page }) => {
  const pvc = catalog.categories.find(category => category.slug === 'pvc-plastic-charms').products[0];
  for (const [sku, category] of [['RW5306', 'Slime Charms'], ['YM109', 'Glitter & Fillers'],
    ['CZB23106', 'Beads for Pens'], [pvc.sku, 'PVC Plastic Charms']]) {
    await page.goto('quote.html?sku=' + encodeURIComponent(sku));
    await expect(page.locator('select[name="product"]')).toHaveValue(category);
    await expect(page.locator('#hiddenSku')).toHaveValue(sku);
  }
  await page.goto('quote.html?sku=RW-UNLISTED-QA');
  await page.waitForLoadState('networkidle');
  await expect(page.locator('select[name="product"]')).toHaveValue('');
});

test('delayed catalog loading preserves a buyer selection or explicit clear', async ({ page }) => {
  let release;
  const held = new Promise(resolve => { release = resolve; });
  await page.route('**/assets/data/product-catalog.json', async route => {
    await held;
    await route.fulfill({ contentType: 'application/json', body: catalogText });
  });
  await page.goto('quote.html?sku=RW5306', { waitUntil: 'domcontentloaded' });
  const category = page.locator('select[name="product"]');
  await category.selectOption('Resin Charms');
  await category.selectOption('');
  release();
  await page.waitForLoadState('networkidle');
  await expect(category).toHaveValue('');
  await category.selectOption('Glitter & Fillers');
  await expect(category).toHaveValue('Glitter & Fillers');
});

test('catalog failure leaves manual category choice and inquiry fields usable', async ({ page }) => {
  await page.route('**/assets/data/product-catalog.json', route => route.fulfill({ status: 503, body: 'Unavailable' }));
  await page.goto('quote.html?sku=RW5306');
  const category = page.locator('select[name="product"]');
  await expect(category).toHaveValue('');
  await category.selectOption('Slime Charms');
  await page.locator('textarea[name="message"]').fill('QA only: sample availability?');
  await expect(category).toHaveValue('Slime Charms');
  await expect(page.locator('button[type="submit"]')).toBeEnabled();
});

test('all contact-page email and WhatsApp drafts use the current inquiry', async ({ page }) => {
  await page.goto('contact.html');
  const form = page.locator('form[action^="https://formsubmit.co/"]');
  const requirement = 'QA only: sample colors & packing? ✨';
  await form.locator('[name="product_details"]').fill('QA only: selected styles');
  await form.locator('[name="quantity"]').fill('20 packs');
  await form.locator('[name="message"]').fill(requirement);
  const bodies = () => page.locator('a[href]').evaluateAll(links => links.flatMap(link => {
    const url = new URL(link.href);
    if (url.protocol === 'mailto:' && url.pathname === 'sales@qulacrafts.com') return [url.searchParams.get('body') || ''];
    if (url.hostname === 'wa.me' && url.pathname === '/8618632026595') return [url.searchParams.get('text') || ''];
    return [];
  }));
  expect((await bodies()).length).toBeGreaterThanOrEqual(7);
  for (const body of await bodies()) {
    expect(body).toContain(requirement);
    expect(body).toContain('20 packs');
    expect(body).toContain('QA only: selected styles');
  }
  await form.locator('[name="message"]').fill('QA only: revised request');
  for (const body of await bodies()) {
    expect(body).not.toContain(requirement);
    expect(body).toContain('QA only: revised request');
  }
  await form.locator('[name="message"]').fill('QA only: long requirements. '.repeat(150));
  await expect(form.locator('[data-inquiry-direct-status]')).toBeVisible();
  await form.locator('[name="message"]').fill('');
  await expect(form.locator('[data-inquiry-direct-status]')).toBeHidden();
});
