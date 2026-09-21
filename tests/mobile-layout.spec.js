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

  const bagBox = await bag.boundingBox();
  expect(bagBox).not.toBeNull();
  expect(bagBox.x).toBeGreaterThanOrEqual(-1);
  expect(right(bagBox)).toBeLessThanOrEqual(391);

  await expect(bag.locator('h3')).toContainText('Bag Charms');
  await expect(bag.locator('a.btn')).toHaveAttribute('href', 'quote.html?application=Bag%20Charms');

  const fixedBar = page.locator('.mobile-cta-bar');
  await expect(fixedBar).toBeVisible();

  await page.screenshot({ path: 'test-results/qula-mobile-bag-charms.png', fullPage: true });
});
