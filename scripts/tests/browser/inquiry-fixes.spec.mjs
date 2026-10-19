import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

// Run with playwright.products.config.mjs (375, 414 and 1440 px).
// Every external request is aborted; direct email/WhatsApp links are only decoded.
const catalog = JSON.parse(readFileSync(new URL('../../../assets/data/product-catalog.json', import.meta.url), 'utf8'));
const products = catalog.categories.flatMap(category => category.products);
const bySku = sku => products.find(product => product.sku === sku);
const firstSku = 'RW26808';
const secondSku = 'RW20809';
const savedSku = 'MA612';
const inquiryAttempts = new WeakMap();

test.beforeEach(async ({ context, page, baseURL }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  const localOrigin = new URL(baseURL).origin;
  const attempts = [];
  inquiryAttempts.set(page, attempts);
  await context.route('**/*', async route => {
    const request = route.request();
    const url = new URL(request.url());
    if (/(^|\.)formsubmit\.co$/i.test(url.hostname) || /\/api\/inquiry\/?$/.test(url.pathname)) attempts.push(request.url());
    if (url.origin !== localOrigin || request.method() !== 'GET') return route.abort();
    return route.continue();
  });
  await page.addInitScript(() => {
    window.__inquiryNativeSubmits = [];
    // A regression in the preview guard cannot send a native multipart request.
    HTMLFormElement.prototype.submit = function () {
      window.__inquiryNativeSubmits.push(this.action);
    };
  });
});

async function seedBasket(page, skus) {
  await page.goto('quote.html', { waitUntil: 'domcontentloaded' });
  await page.evaluate(items => localStorage.setItem('qcBasket', JSON.stringify(items)), skus.map(sku => ({
    sku, image: bySku(sku).image,
  })));
}

async function basketSkus(page) {
  return page.evaluate(() => JSON.parse(localStorage.getItem('qcBasket') || '[]').map(item => item.sku));
}

async function tabToNativeButton(page, button) {
  await expect(button).toBeVisible();
  await expect(button).toHaveJSProperty('tagName', 'BUTTON');
  await expect(button).toHaveAttribute('type', 'button');
  await button.focus();
  await page.keyboard.press('Shift+Tab');
  await expect(button).not.toBeFocused();
  await page.keyboard.press('Tab');
  await expect(button).toBeFocused();
}

async function expectUsefulFocus(page) {
  await expect.poll(() => page.evaluate(() => !!document.activeElement?.matches(
    '.bp-remove, .bp-clear, textarea[name="message"]',
  ))).toBe(true);
}

async function directBodies(page) {
  const hrefs = await page.locator('[data-inquiry-direct]').evaluateAll(
    links => links.map(link => ({ kind: link.dataset.inquiryDirect, href: link.href })),
  );
  // Form email/WhatsApp, footer email/WhatsApp, mobile action and floating action.
  expect(hrefs).toHaveLength(6);
  expect(hrefs.filter(link => link.kind === 'email')).toHaveLength(2);
  expect(hrefs.filter(link => link.kind === 'whatsapp')).toHaveLength(4);
  return hrefs.map(({ kind, href }) => {
    const url = new URL(href);
    if (kind === 'email') expect(url.pathname).toBe('sales@qulacrafts.com');
    else expect(url.hostname).toBe('wa.me');
    return { kind, href, body: url.searchParams.get(kind === 'email' ? 'body' : 'text') || '' };
  });
}

async function expectBodiesContain(page, values) {
  for (const value of values) {
    await expect.poll(async () => (await directBodies(page)).every(link => link.body.includes(value))).toBe(true);
  }
}

async function assertNoSend(page) {
  expect(inquiryAttempts.get(page)).toEqual([]);
  expect(await page.evaluate(() => window.__inquiryNativeSubmits)).toEqual([]);
  expect(await page.evaluate(() => sessionStorage.getItem('qula_pending_inquiry_v1'))).toBeNull();
  expect(await page.evaluate(() => (window.dataLayer || []).filter(event => event[0] === 'event' && event[1] === 'generate_lead'))).toEqual([]);
}

test('static and search buttons support Tab, Enter, Space, deduplication, remove and clear', async ({ page }) => {
  await page.goto('resin-charms.html', { waitUntil: 'domcontentloaded' });
  expect(await page.locator('.basket-add').evaluateAll(buttons => buttons.every(button => button.tagName === 'BUTTON' && button.type === 'button'))).toBe(true);
  const staticAdd = page.locator(`.basket-add[data-sku="${firstSku}"]`).first();
  await tabToNativeButton(page, staticAdd);
  await page.keyboard.press('Enter');
  await expect.poll(() => basketSkus(page)).toEqual([firstSku]);
  await staticAdd.press('Space');
  expect(await basketSkus(page)).toEqual([firstSku]);

  await page.goto(`products.html?search=${secondSku}`, { waitUntil: 'domcontentloaded' });
  const dynamicAdd = page.locator('[data-search-results] .basket-add').first();
  await expect(dynamicAdd).toHaveAttribute('data-sku', secondSku);
  await tabToNativeButton(page, dynamicAdd);
  await page.keyboard.press('Space');
  await expect.poll(() => basketSkus(page)).toEqual([firstSku, secondSku]);
  await dynamicAdd.press('Enter');
  expect(await basketSkus(page)).toEqual([firstSku, secondSku]);

  await page.goto('quote.html', { waitUntil: 'domcontentloaded' });
  await expect(page.locator('.basket-panel li')).toHaveCount(2);
  const remove = page.locator(`.bp-remove[data-sku="${firstSku}"]`);
  await expect(remove).toHaveAttribute('aria-label', new RegExp(firstSku));
  await tabToNativeButton(page, remove);
  await page.keyboard.press('Enter');
  await expect(page.locator('.basket-panel li')).toHaveCount(1);
  await expectUsefulFocus(page);
  expect(await basketSkus(page)).toEqual([secondSku]);

  const clear = page.locator('.bp-clear');
  await expect(clear).toHaveAttribute('aria-label', /clear/i);
  await tabToNativeButton(page, clear);
  await page.keyboard.press('Space');
  await expect(page.locator('.basket-panel')).toHaveCount(0);
  expect(await basketSkus(page)).toEqual([]);
  await expectUsefulFocus(page);
  await assertNoSend(page);
});

test('direct links include the URL product, saved list and every current requirement without losing Unicode or ampersands', async ({ page }, testInfo) => {
  await seedBasket(page, [savedSku, secondSku]);
  const title = `${firstSku} Glitter & Sequins 雪`;
  const query = new URLSearchParams({ sku: firstSku, product: title, category: 'Resin Charms', image: bySku(firstSku).image, entry_page: '/' + bySku(firstSku).pdp });
  await page.goto('quote.html?' + query, { waitUntil: 'domcontentloaded' });
  await expect(page.locator('.basket-panel li')).toHaveCount(2);
  await expect(page.locator('[name="selected_sku"]')).toHaveValue(firstSku);
  await expect(page.locator('#pPreviewTitle')).toHaveText(title);
  await expect(page.locator('header a.nav-link[href="about.html"]')).not.toHaveClass(/\bactive\b/);

  const fields = {
    product_details: 'mix & 2 mm', quantity: '200 pcs', country: '日本', application: 'DIY & slime',
    custom: '青 & gold', packaging: 'pouch & logo', target_delivery_date: '2027-01-12',
    name: 'Zoë 雪', company: 'A & B', email: 'buyer+qa@example.com',
  };
  for (const [name, value] of Object.entries(fields)) await page.locator(`#inquiryForm [name="${name}"]`).fill(value);
  await page.locator('[name="product"]').selectOption('Resin Charms');
  await page.locator('[name="message"]').fill('Please quote 雪 & stars.\n- Keep my own bullet.');
  await expectBodiesContain(page, [firstSku, savedSku, secondSku, title, 'Resin Charms', ...Object.values(fields), 'Please quote 雪 & stars.', '- Keep my own bullet.']);
  for (const link of await directBodies(page)) expect(link.body).not.toContain('&amp;');

  await page.locator('[data-reply-method="WhatsApp"]').click();
  await page.locator('[name="whatsapp"]').fill('+12025550123');
  await expectBodiesContain(page, ['WhatsApp', '+12025550123']);
  const typedMessage = 'Changed only by typing: 香 & 星; literal &amp; stays literal.';
  await page.locator('[name="message"]').fill(typedMessage);
  await expectBodiesContain(page, [typedMessage, firstSku, savedSku, secondSku, title]);
  for (const link of await directBodies(page)) {
    expect(link.body).not.toContain('Please quote 雪 & stars.');
    expect(link.body).not.toContain('&amp;amp;');
  }
  expect(await basketSkus(page)).toEqual([savedSku, secondSku]);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: testInfo.outputPath('quote-context-top.png'), fullPage: false, animations: 'disabled' });
  await page.screenshot({ path: testInfo.outputPath('quote-context.png'), fullPage: true, animations: 'disabled' });
  await assertNoSend(page);
});

test('removing or clearing synchronizes every direct link while preserving edited SKU quantities and customer notes', async ({ page }) => {
  await seedBasket(page, [firstSku, secondSku]);
  await page.goto('quote.html', { waitUntil: 'domcontentloaded' });
  await expect(page.locator('.basket-panel li')).toHaveCount(2);
  const ownBullet = '- Keep my custom mix: 雪 & stars';
  const note = 'Please pack separately.\n- My own packaging request.';
  await page.locator('[name="message"]').fill(`Inquiry list:\n- ${firstSku}: 700 pcs\n- ${secondSku}: 200 packs\n${ownBullet}\n\n${note}`);
  await expectBodiesContain(page, [`${firstSku}: 700 pcs`, `${secondSku}: 200 packs`, ownBullet, note]);
  await page.locator(`.bp-remove[data-sku="${firstSku}"]`).press('Space');
  await expect(page.locator('.basket-panel li')).toHaveCount(1);
  await expect(page.locator('[name="message"]')).not.toHaveValue(new RegExp(firstSku));
  for (const text of [`${secondSku}: 200 packs`, ownBullet, note]) await expect(page.locator('[name="message"]')).toHaveValue(new RegExp(text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  await expectBodiesContain(page, [`${secondSku}: 200 packs`, ownBullet, note]);
  for (const link of await directBodies(page)) expect(link.body).not.toContain(firstSku);
  await expectUsefulFocus(page);

  await page.locator('.bp-clear').press('Enter');
  await expect(page.locator('.basket-panel')).toHaveCount(0);
  for (const text of [ownBullet, note]) expect(await page.locator('[name="message"]').inputValue()).toContain(text);
  expect(await page.locator('[name="message"]').inputValue()).not.toContain(secondSku);
  await expectBodiesContain(page, [ownBullet, note]);
  for (const link of await directBodies(page)) {
    expect(link.body).not.toContain(firstSku);
    expect(link.body).not.toContain(secondSku);
  }
  await expectUsefulFocus(page);
});

test('URL-selected product remains after the saved list is cleared', async ({ page }) => {
  await seedBasket(page, [secondSku, savedSku]);
  await page.goto('quote.html?' + new URLSearchParams({ sku: firstSku, product: firstSku + ' Selected acorn', entry_page: '/' + bySku(firstSku).pdp }));
  await expect(page.locator('.bp-clear')).toBeVisible();
  const ownQuestion = 'Keep my own selected-product question & literal &amp;.';
  await page.locator('[name="message"]').fill(ownQuestion);
  await page.locator('.bp-clear').press('Enter');
  await expect(page.locator('.basket-panel')).toHaveCount(0);
  await expect(page.locator('[name="selected_sku"]')).toHaveValue(firstSku);
  await expectBodiesContain(page, [firstSku, ownQuestion]);
  for (const link of await directBodies(page)) {
    expect(link.body).not.toContain(secondSku);
    expect(link.body).not.toContain(savedSku);
  }
});

test('overlong direct links keep the complete text, show a hint and prevent launch', async ({ context, page }) => {
  await page.goto('quote.html', { waitUntil: 'domcontentloaded' });
  const message = 'Long requirement '.repeat(180) + ' END-雪-&';
  await page.locator('[name="message"]').fill(message);
  for (const link of await directBodies(page)) {
    expect(link.href.length).toBeGreaterThan(2000);
    expect(link.body).toContain(message);
  }
  const status = page.locator('[data-inquiry-direct-status]');
  await expect(status).toBeVisible();
  await expect(status).toContainText(/long|copy|2,?000/i);
  const originalURL = page.url();
  const originalPageCount = context.pages().length;
  const visibleLinks = page.locator('[data-inquiry-direct]:visible');
  const visibleLinkCount = await visibleLinks.count();
  expect(visibleLinkCount).toBeGreaterThanOrEqual(4);
  for (let index = 0; index < visibleLinkCount; index++) {
    // Observe the app's cancellation, then always cancel at the final bubble stage.
    // Even a failing assertion cannot open an email client or WhatsApp.
    await page.evaluate(() => {
      window.__directWasPrevented = null;
      window.addEventListener('click', event => {
        if (!event.target.closest('[data-inquiry-direct]')) return;
        window.__directWasPrevented = event.defaultPrevented;
        event.preventDefault();
      }, { once: true });
    });
    await visibleLinks.nth(index).press('Enter');
    expect(await page.evaluate(() => window.__directWasPrevented)).toBe(true);
    expect(page.url()).toBe(originalURL);
    expect(context.pages()).toHaveLength(originalPageCount);
  }
  await page.locator('[name="message"]').fill('Short question');
  await expectBodiesContain(page, ['Short question']);
  await expect.poll(async () => status.count().then(async count => count === 0 || !(await status.isVisible()) || !(await status.textContent())?.trim())).toBe(true);
  await assertNoSend(page);
});

test('selecting and removing a reference file updates every direct-link attachment reminder', async ({ page }) => {
  await page.goto('quote.html', { waitUntil: 'domcontentloaded' });
  const form = page.locator('#inquiryForm');
  const reminder = 'Reference files: please attach them separately to this message.';
  await form.locator('[name="message"]').fill('Reference shape: 雪 & stars; literal &amp;.');
  for (const link of await directBodies(page)) expect(link.body).not.toContain(reminder);
  await form.locator('.file-input-multi').setInputFiles({
    name: 'reference-雪-and-stars.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4\n% Preview attachment fixture\n'),
  });
  await expect(form.locator('.file-list .file-item')).toHaveCount(1);
  await expectBodiesContain(page, [reminder, 'Reference shape: 雪 & stars; literal &amp;.']);
  await form.locator('.file-list .file-remove').click();
  await expect(form.locator('.file-list .file-item')).toHaveCount(0);
  await expect.poll(async () => (await directBodies(page)).every(link => !link.body.includes(reminder))).toBe(true);
  await expectBodiesContain(page, ['Reference shape: 雪 & stars; literal &amp;.']);
  await assertNoSend(page);
});

test('reply validation, attachment limit and preview submission guards remain effective', async ({ page }) => {
  await seedBasket(page, [firstSku]);
  await page.goto('quote.html', { waitUntil: 'domcontentloaded' });
  await expect(page.locator('.basket-panel li')).toHaveCount(1);
  const form = page.locator('#inquiryForm');
  const email = form.locator('[name="email"]');
  const phone = form.locator('[name="whatsapp"]');
  await expect(email).toBeEnabled();
  await expect(email).toHaveJSProperty('required', true);
  await expect(phone).toBeDisabled();
  await form.locator('[name="message"]').fill('Preview only, do not send.');
  await email.fill('invalid-email');
  expect(await form.evaluate(element => element.checkValidity())).toBe(false);
  await email.fill('buyer@example.com');
  expect(await form.evaluate(element => element.checkValidity())).toBe(true);

  await form.locator('[data-reply-method="WhatsApp"]').click();
  await expect(email).toBeDisabled();
  await expect(phone).toBeEnabled();
  await expect(phone).toHaveJSProperty('required', true);
  await phone.fill('12345');
  expect(await form.evaluate(element => element.checkValidity())).toBe(false);
  await phone.fill('+12025550123');
  expect(await form.evaluate(element => element.checkValidity())).toBe(true);
  await form.locator('button[type="submit"]').click();
  await expect(form.locator('[data-preview-submit-status]')).toContainText('inquiry sending is disabled');
  await assertNoSend(page);
  expect(await basketSkus(page)).toEqual([firstSku]);
  await expect(form.locator('button[type="submit"]')).toBeEnabled();

  await form.locator('.file-input-multi').setInputFiles({ name: 'too-large.png', mimeType: 'image/png', buffer: Buffer.alloc(11 * 1024 * 1024) });
  await expect(form.locator('.attachment-status')).toContainText('exceeds the 10MB total limit');
  await form.locator('button[type="submit"]').click();
  await assertNoSend(page);
  expect(await basketSkus(page)).toEqual([firstSku]);
});

test('all current catalog groups and exact RW26808/RW20809 searches remain available', async ({ page }) => {
  expect(catalog.totalProducts).toBe(products.length);
  expect(new Set(products.map(product => product.pdp)).size).toBe(products.length);
  await page.goto('products.html', { waitUntil: 'domcontentloaded' });
  const response = await page.request.get('assets/data/product-catalog.json');
  expect(response.ok()).toBe(true);
  const browserCatalog = await response.json();
  expect(browserCatalog.totalProducts).toBe(catalog.totalProducts);
  expect(browserCatalog.categories.flatMap(category => category.products)).toHaveLength(products.length);
  for (const sku of [firstSku, secondSku]) {
    await page.locator('[data-catalog-search]').fill(sku);
    const result = page.locator('[data-search-results] .product-card').first();
    await expect(result.locator('.basket-add')).toHaveAttribute('data-sku', sku);
    await expect(result.locator('h3 a')).toHaveAttribute('href', bySku(sku).pdp);
    await expect(result.locator('h3')).toHaveText(bySku(sku).title);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
  }
});
