const { test, expect } = require('@playwright/test');

test.use({
  viewport: { width: 390, height: 844 },
  isMobile: true,
  hasTouch: true,
  deviceScaleFactor: 1
});

const baseURL = 'http://127.0.0.1:4173';

async function expectNoHorizontalOverflow(page) {
  const dims = await page.evaluate(() => ({
    innerWidth: window.innerWidth,
    docWidth: document.documentElement.scrollWidth
  }));
  expect(dims.docWidth).toBeLessThanOrEqual(dims.innerWidth + 1);
}

function right(box) { return box.x + box.width; }
function bottom(box) { return box.y + box.height; }

test('mobile product menu is full-height, scrollable and complete', async ({ page }) => {
  await page.goto(baseURL + '/polymer-clay-sprinkles.html', { waitUntil: 'networkidle' });
  await page.locator('[data-nav-toggle]').click();

  const nav = page.locator('[data-nav-menu]');
  await expect(nav).toHaveClass(/open/);
  await expect(nav).toBeVisible();

  const metrics = await nav.evaluate((el) => {
    const r = el.getBoundingClientRect();
    return {
      top: r.top,
      left: r.left,
      right: r.right,
      bottom: r.bottom,
      height: r.height,
      clientHeight: el.clientHeight,
      scrollHeight: el.scrollHeight,
      overflowY: getComputedStyle(el).overflowY
    };
  });

  expect(metrics.height).toBeGreaterThan(340);
  expect(metrics.clientHeight).toBeGreaterThan(330);
  expect(metrics.left).toBeGreaterThanOrEqual(0);
  expect(metrics.right).toBeLessThanOrEqual(390);
  expect(['auto', 'scroll']).toContain(metrics.overflowY);

  const productLinks = page.locator('.nav-sub-link');
  expect(await productLinks.count()).toBeGreaterThanOrEqual(10);
  await expect(productLinks.filter({ hasText: 'Slime Charms' })).toBeVisible();
  await expect(productLinks.filter({ hasText: 'Polymer Clay Sprinkles' })).toBeVisible();

  await page.screenshot({ path: 'test-results/qula-mobile-menu-top.png' });

  const scrollResult = await nav.evaluate((el) => {
    const before = el.scrollTop;
    el.scrollTop = el.scrollHeight;
    return {
      before,
      after: el.scrollTop,
      max: el.scrollHeight - el.clientHeight
    };
  });
  expect(scrollResult.max).toBeGreaterThan(100);
  expect(scrollResult.after).toBeGreaterThan(100);

  await page.waitForTimeout(150);
  const quote = nav.locator(':scope > .btn').last();
  await expect(quote).toBeVisible();
  const quoteBox = await quote.boundingBox();
  expect(quoteBox).not.toBeNull();
  expect(bottom(quoteBox)).toBeLessThanOrEqual(844 - 52 + 4);

  await page.screenshot({ path: 'test-results/qula-mobile-menu-bottom.png' });
  await expectNoHorizontalOverflow(page);
});

test('mobile fixed CTA keeps Get Quote and WhatsApp fully visible', async ({ page }) => {
  await page.goto(baseURL + '/resin-charms.html', { waitUntil: 'networkidle' });
  const bar = page.locator('.mobile-cta-bar');
  await expect(bar).toBeVisible();

  const result = await bar.evaluate((el) => {
    const r = el.getBoundingClientRect();
    const children = [...el.querySelectorAll('a')].map((a) => {
      const b = a.getBoundingClientRect();
      return { text: a.textContent.trim(), left: b.left, right: b.right, width: b.width };
    });
    return { left: r.left, right: r.right, width: r.width, children };
  });

  expect(result.left).toBeGreaterThanOrEqual(0);
  expect(result.right).toBeLessThanOrEqual(390);
  expect(result.width).toBeGreaterThanOrEqual(389);
  expect(result.children).toHaveLength(2);
  expect(result.children[0].text).toBe('Get Quote');
  expect(result.children[1].text).toBe('WhatsApp');
  expect(result.children[0].width).toBeGreaterThan(185);
  expect(result.children[1].width).toBeGreaterThan(185);
  expect(Math.abs(result.children[0].width - result.children[1].width)).toBeLessThanOrEqual(2);

  await page.screenshot({ path: 'test-results/qula-mobile-fixed-cta.png' });
  await expectNoHorizontalOverflow(page);
});

test('mobile PDP stays within viewport and remains readable', async ({ page }) => {
  await page.goto(baseURL + '/p-rw26774.html', { waitUntil: 'networkidle' });
  await expectNoHorizontalOverflow(page);

  const selectors = ['.pdp-hero h1', '.detail-grid', '.gallery-main img', '.spec-table', '.pdp-cta'];
  for (const selector of selectors) {
    const loc = page.locator(selector).first();
    await expect(loc).toBeVisible();
    const box = await loc.boundingBox();
    expect(box).not.toBeNull();
    expect(box.x).toBeGreaterThanOrEqual(-1);
    expect(right(box)).toBeLessThanOrEqual(391);
  }

  const cta = page.locator('.pdp-cta');
  const ctaButtons = cta.locator('a');
  expect(await ctaButtons.count()).toBeGreaterThanOrEqual(3);
  for (let i = 0; i < await ctaButtons.count(); i++) {
    const box = await ctaButtons.nth(i).boundingBox();
    expect(box).not.toBeNull();
    expect(box.width).toBeGreaterThan(300);
    expect(right(box)).toBeLessThanOrEqual(391);
  }

  await page.screenshot({ path: 'test-results/qula-mobile-pdp.png', fullPage: true });
});


test('Bag Charms applications update fits the current mobile layout', async ({ page }) => {
  await page.goto(baseURL + '/applications.html', { waitUntil: 'networkidle' });
  await expectNoHorizontalOverflow(page);

  const cards = page.locator('.applications-v3-card');
  await expect(cards).toHaveCount(9);

  const bag = page.locator('#bag-charms');
  await expect(bag).toBeAttached();
  await bag.scrollIntoViewIfNeeded();
  await expect(bag).toBeVisible();
  await page.waitForTimeout(1200);

  const bagBox = await bag.boundingBox();
  expect(bagBox).not.toBeNull();
  expect(bagBox.x).toBeGreaterThanOrEqual(-1);
  expect(right(bagBox)).toBeLessThanOrEqual(391);

  await expect(bag.locator('h3')).toContainText('Bag Charms');
  const inquiryUrl = new URL(await bag.locator('a.btn').getAttribute('href'), page.url());
  expect(inquiryUrl.origin).toBe(new URL(page.url()).origin);
  expect(inquiryUrl.pathname).toBe('/quote.html');
  expect(inquiryUrl.searchParams.get('application')).toBe('Bag Charms');
  expect(inquiryUrl.searchParams.get('entry_page')).toBe('/applications.html');

  const fixedBar = page.locator('.mobile-cta-bar');
  await expect(fixedBar).toBeVisible();

  await bag.screenshot({ path: 'test-results/qula-mobile-bag-charms-card.png' });
  await page.screenshot({ path: 'test-results/qula-mobile-bag-charms.png', fullPage: true });
});

const currentBatch = require('../scripts/data/qula-products-20261012-v3.json');
const quoteCategories = {
  'plastic-beads': 'Acrylic Beads',
  'jewelry-accessories': 'Jewelry Accessories',
  'polymer-clay-slices': 'Polymer Clay Sprinkles',
  'plastic-sequins': 'Glitter & Fillers',
  keychain: 'Keychains',
  'slime-charms': 'Slime Charms',
  'resin-charms': 'Resin Charms'
};

async function expectElementFits(locator, width) {
  await expect(locator).toBeVisible();
  const box = await locator.boundingBox();
  expect(box).not.toBeNull();
  expect(box.x).toBeGreaterThanOrEqual(-1);
  expect(right(box)).toBeLessThanOrEqual(width + 1);
}

for (const size of [
  { width: 360, height: 800 },
  { width: 375, height: 812 },
  { width: 390, height: 844 },
  { width: 414, height: 896 }
]) {
  test(`current product batch and inquiry flow fit a ${size.width}px touch screen`, async ({ page }) => {
    test.setTimeout(180000);
    await page.setViewportSize(size);
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));

    for (const path of [
      'index.html', 'products.html', 'resin-charms.html',
      'acrylic-beads.html', 'polymer-clay-sprinkles.html',
      'factory.html', 'quote.html'
    ]) {
      await test.step(`core page: ${path}`, async () => {
        await page.goto(`${baseURL}/${path}`, { waitUntil: 'networkidle' });
        await expectNoHorizontalOverflow(page);
        await expectElementFits(page.locator('main h1'), size.width);
        const fixedBar = page.locator('.mobile-cta-bar');
        await expectElementFits(fixedBar, size.width);
        for (const button of await fixedBar.locator('a').all()) {
          await expectElementFits(button, size.width);
          const box = await button.boundingBox();
          expect(box.height).toBeGreaterThanOrEqual(40);
          expect(bottom(box)).toBeLessThanOrEqual(size.height + 1);
        }
        if (path === 'index.html') {
          await page.screenshot({ path: `test-results/qula-mobile-${size.width}-home.png` });
        }
      });
    }

    await page.goto(`${baseURL}/products.html`, { waitUntil: 'networkidle' });
    await page.locator('[data-nav-toggle]').tap();
    const nav = page.locator('[data-nav-menu]');
    await expect(nav).toHaveClass(/open/);
    await expectElementFits(nav, size.width);
    expect(await nav.locator('.nav-sub-link').count()).toBeGreaterThanOrEqual(10);
    await nav.evaluate(el => { el.scrollTop = el.scrollHeight; });
    const menuQuote = nav.locator(':scope > .btn').last();
    await expect(menuQuote).toBeVisible();
    const menuQuoteBox = await menuQuote.boundingBox();
    expect(bottom(menuQuoteBox)).toBeLessThanOrEqual(size.height - 48);
    await page.screenshot({ path: `test-results/qula-mobile-${size.width}-menu.png` });
    await page.locator('[data-nav-toggle]').tap();
    await expect(nav).not.toHaveClass(/open/);

    const search = page.getByRole('searchbox', { name: 'Search product catalog' });
    await search.fill('RW5463');
    const results = page.locator('[data-search-results]');
    await expect(results.locator('.product-card')).toHaveCount(1);
    await expect(results).toContainText('RW5463');
    await expectNoHorizontalOverflow(page);

    const quoteUrls = new Map();
    for (const product of currentBatch) {
      await test.step(`product: ${product.sku}`, async () => {
        await page.goto(`${baseURL}/p-${product.key}.html`, { waitUntil: 'networkidle' });
        await expectNoHorizontalOverflow(page);
        for (const selector of ['.pdp-hero h1', '.detail-grid', '.gallery-main img', '.spec-table', '.pdp-cta']) {
          await expectElementFits(page.locator(selector).first(), size.width);
        }
        const gallery = page.locator('.gallery-main img, .gallery-row img');
        await expect(gallery).toHaveCount(3);
        await page.locator('.gallery-row').scrollIntoViewIfNeeded();
        await expect.poll(() => gallery.evaluateAll(images => images.every(img => img.complete && img.naturalWidth > 0))).toBe(true);
        expect(await gallery.evaluateAll(images => images.every(img => getComputedStyle(img).objectFit === 'contain'))).toBe(true);
        const cta = page.locator('.pdp-cta .btn-primary');
        await expectElementFits(cta, size.width);
        const box = await cta.boundingBox();
        expect(box.height).toBeGreaterThanOrEqual(40);
        const url = new URL(await cta.getAttribute('href'), page.url());
        expect(url.searchParams.get('sku')).toBe(product.sku);
        expect(url.searchParams.get('category')).toBe(quoteCategories[product.category]);
        const firstInCategory = !quoteUrls.has(product.category);
        if (firstInCategory) quoteUrls.set(product.category, url.href);
        if (['rw1672-rw2072-rw3492-rw20104', 'sd144'].includes(product.key)) {
          await page.screenshot({ path: `test-results/qula-mobile-${size.width}-${product.key}.png`, fullPage: true });
        }
        if (firstInCategory) {
          await cta.tap();
          await expect(page).toHaveURL(/\/quote\.html\?/);
          await expect(page.locator('#product')).toHaveValue(quoteCategories[product.category]);
          await expect(page.locator('#pPreviewTitle')).toContainText(product.sku);
        }
      });
    }

    for (const [category, url] of quoteUrls) {
      await test.step(`inquiry: ${category}`, async () => {
        await page.goto(url, { waitUntil: 'networkidle' });
        const sku = new URL(url).searchParams.get('sku');
        await expectNoHorizontalOverflow(page);
        await expect(page.locator('#product')).toHaveValue(quoteCategories[category]);
        await expect(page.locator('#pPreviewTitle')).toContainText(sku);
        await expect(page.locator('#message')).toHaveValue(new RegExp(sku.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
        await expect.poll(() => page.locator('#pPreviewImg').evaluate(img => img.complete && img.naturalWidth > 0)).toBe(true);
        await expect(page.locator('#inquiryForm')).toHaveAttribute('method', /post/i);
        await expect(page.locator('#inquiryForm')).toHaveAttribute('enctype', 'multipart/form-data');
        for (const field of await page.locator('#inquiryForm input:not([type=hidden]):not([type=file]), #inquiryForm select, #inquiryForm textarea').all()) {
          if (await field.isVisible()) await expectElementFits(field, size.width);
        }
        if (category === 'jewelry-accessories') {
          await page.screenshot({ path: `test-results/qula-mobile-${size.width}-quote.png`, fullPage: true });
        }
      });
    }

    await page.goto(`${baseURL}/p-cdk004448.html`, { waitUntil: 'networkidle' });
    await page.locator('.gallery-row img').first().tap();
    await expect(page.locator('.ux-lightbox')).toHaveAttribute('aria-hidden', 'false');
    await page.getByRole('button', { name: 'Close image', exact: true }).tap();
    await expect(page.locator('.ux-lightbox')).toHaveAttribute('aria-hidden', 'true');

    await page.goto(`${baseURL}/p-rw1672-rw2072-rw3492-rw20104.html`, { waitUntil: 'networkidle' });
    await page.locator('.pdp-cta .basket-add').tap();
    await page.locator('.basket-chip').tap();
    await expect(page.locator('.basket-panel')).toContainText('RW1672/RW2072/RW3492/RW20104');
    await expect(page.locator('#message')).toHaveValue(/RW1672\/RW2072\/RW3492\/RW20104/);
    await expect.poll(() => page.locator('.basket-panel img').evaluate(img => img.complete && img.naturalWidth > 0)).toBe(true);
    await expectNoHorizontalOverflow(page);
    await page.locator('.bp-remove').tap();
    await expect(page.locator('.basket-panel')).toHaveCount(0);
    await expect(page.locator('#message')).toHaveValue('');
    expect(errors).toEqual([]);
    console.log(JSON.stringify({ width: size.width, height: size.height, products: currentBatch.length, galleryImages: currentBatch.length * 3, inquiryCategories: quoteUrls.size, result: 'passed', submitted: false }));
  });
}
