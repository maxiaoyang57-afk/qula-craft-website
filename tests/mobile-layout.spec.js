const { test, expect } = require('@playwright/test');

test.use({
  viewport: { width: 390, height: 844 },
  isMobile: true,
  hasTouch: true,
  deviceScaleFactor: 1
});

const baseURL = 'http://127.0.0.1:4173';

const supplement = require('../docs/product-batch-manifest-20261016-supplement.json');
const supplementCatalog = require('../assets/data/product-catalog.json').categories.flatMap(category => category.products);

for (const width of [360, 390, 768]) {
  test(`all 20 supplemental products keep images, full SKU and inquiry context at ${width}px`, async ({ page }) => {
    test.setTimeout(180000);
    await page.setViewportSize({ width, height: 900 });
    await page.route(/(?:formsubmit\.co|google-analytics\.com|clarity\.ms)/, route => route.abort());
    for (const record of supplement.products) {
      const product = supplementCatalog.find(item => item.sku === record.sku);
      await page.goto(baseURL + '/' + record.pdp, { waitUntil: 'domcontentloaded' });
      await expect(page.locator('h1')).toHaveText(product.title);
      await expectNoHorizontalOverflow(page);
      const gallery = page.locator('.gallery-main img, .gallery-row img');
      await expect(gallery).toHaveCount(3);
      for (let i = 0; i < 3; i++) {
        await gallery.nth(i).scrollIntoViewIfNeeded();
        await expect.poll(() => gallery.nth(i).evaluate(img => img.complete && img.naturalWidth > 0)).toBe(true);
        expect(await gallery.nth(i).getAttribute('src')).toBe(record.imageOutputs[i].path);
        expect(await gallery.nth(i).evaluate(img => getComputedStyle(img).objectFit)).toBe('contain');
      }
      const direct = new URL(await page.locator('.pdp-cta .btn-primary').getAttribute('href'), page.url());
      for (const selector of ['.site-header .main-nav > .btn', '.footer-actions .btn-primary', '.mobile-cta-bar .mcb-quote']) {
        const link = page.locator(selector);
        await expect(link).toHaveAttribute('href', /[?&]sku=/);
        const target = new URL(await link.getAttribute('href'), page.url());
        for (const key of ['sku', 'product', 'category', 'image']) expect(target.searchParams.get(key)).toBe(direct.searchParams.get(key));
      }
      const basket = new URL(await page.locator('.basket-chip').getAttribute('href'), page.url());
      expect(basket.searchParams.has('sku')).toBe(false);
      await page.locator('.pdp-cta .btn-primary').click();
      await expect(page.locator('#hiddenSku')).toHaveValue(record.sku);
      await expect(page.locator('#pPreviewImg')).toHaveAttribute('src', '/' + record.imageOutputs[0].path);
      await expect(page.locator('select[name="product"]')).toHaveValue(direct.searchParams.get('category'));
      await expectNoHorizontalOverflow(page);
    }
  });
}

test('generic PDP quote selects its own product while a related card keeps its exact SKU', async ({ page }) => {
  await page.goto(baseURL + '/p-rw25208.html');
  const related = page.locator('.product-card').first();
  const relatedSku = await related.locator('.pill').textContent();
  await related.locator('a').first().click();
  const own = new URL(await page.locator('.pdp-cta .btn-primary').getAttribute('href'), page.url());
  expect(own.searchParams.get('sku')).toBe(relatedSku.trim());
  const footer = page.locator('.footer-actions .btn-primary');
  await footer.click();
  await expect(page.locator('#hiddenSku')).toHaveValue(relatedSku.trim());
});

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

test('selected custom design guide shows the full illustration and separate material routes', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  const article = baseURL + '/blog-custom-resin-polymer-clay-process.html';
  const service = baseURL + '/customization.html';

  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: width === 1440 ? 1000 : 844 });
    await page.goto(article, { waitUntil: 'networkidle' });
    await expectNoHorizontalOverflow(page);
    await expect(page.locator('.custom-story h1')).toHaveText('From your idea to a custom craft collection');
    await expect(page.locator('.custom-checkpoint')).toHaveCount(8);
    await expect(page.locator('.custom-story-hero .custom-process-figure')).toHaveCount(1);
    await expect(page.locator('.custom-process-figure figcaption')).toContainText('AI-generated scenes');
    await expect(page.locator('.custom-illustration')).toHaveCount(0);
    await expect(page.locator('.custom-flow')).toHaveCount(0);
    const example = page.locator('.custom-process-figure img');
    await expect(example).toBeVisible();
    await expect.poll(() => example.evaluate(img => img.naturalWidth)).toBe(1536);
    const proportions = await example.evaluate(img => ({
      fit: getComputedStyle(img).objectFit,
      ratio: img.getBoundingClientRect().width / img.getBoundingClientRect().height
    }));
    expect(proportions.fit).toBe('contain');
    expect(Math.abs(proportions.ratio - 1.5)).toBeLessThan(0.02);
    await page.screenshot({ path: `test-results/qula-custom-guide-${width}.png`, fullPage: width === 390 });
    await page.locator('.custom-process-figure').screenshot({ path: `test-results/qula-custom-example-${width}.png` });
    await page.locator('.custom-contents a[href="#sample-development"]').click();
    await expect(page).toHaveURL(/#sample-development$/);
    await expect(page.locator('#sample-development h3')).toHaveCount(2);

    await page.goto(service, { waitUntil: 'networkidle' });
    await expectNoHorizontalOverflow(page);
    await expect(page.locator('.custom-service-card')).toHaveCount(2);
    await page.locator('#material-options').screenshot({ path: `test-results/qula-custom-services-${width}.png` });
  }

  for (const [id, product] of [
    ['resin-customization', 'Resin Charms'],
    ['polymer-customization', 'Polymer Clay Sprinkles']
  ]) {
    await page.goto(service, { waitUntil: 'networkidle' });
    await page.locator('#' + id + ' a.btn').click();
    await expect(page.locator('[name="product"]')).toHaveValue(product);
  }
  // This test only follows quote links. It never submits an inquiry.
});

for (const width of [375, 1440]) {
  test(`category bulk quotes preserve complete names and source at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.route('**/*', route => {
      const request = route.request();
      if (!request.url().startsWith(baseURL) || !['GET', 'HEAD'].includes(request.method())) return route.abort();
      return route.continue();
    });
    const categories = [
      ['polymer-clay-sprinkles.html', 'Polymer Clay Slices & Sprinkles Wholesale', 'Polymer Clay Sprinkles'],
      ['resin-charms.html', 'Bulk Resin Charms & Flatback Cabochons', 'Resin Charms'],
      ['acrylic-beads.html', 'Wholesale Acrylic Beads for Crafts & Bag Charms', 'Acrylic Beads'],
      ['glitter-sequins-fillers.html', 'Glitter Sequins, Craft Fillers & Acrylic Gems', 'Glitter & Fillers']
    ];
    for (const [path, title, category] of categories) {
      await page.goto(baseURL + '/' + path);
      const cta = page.locator('.hero-actions a').filter({ hasText: 'Request Bulk Quote' });
      const target = new URL(await cta.getAttribute('href'), page.url());
      expect(target.searchParams.get('product')).toBe(title);
      expect(target.searchParams.get('entry_title')).toBe(title);
      expect(target.searchParams.get('entry_page')).toBe('/' + path);
      await cta.click();
      await expect(page.locator('#pPreviewTitle')).toHaveText(title);
      await expect(page.locator('select[name="product"]')).toHaveValue(category);
      expect(await page.locator('#message').inputValue()).toContain(title);
      await expect(page.locator('[name="entry_title"]')).toHaveValue(title);
      await expect(page.locator('[name="entry_page"]')).toHaveValue('https://www.qulacrafts.com/' + path);
      await expectNoHorizontalOverflow(page);
    }
  });
}
