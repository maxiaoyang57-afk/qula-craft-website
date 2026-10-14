// Real browser tests with all requests fulfilled locally or aborted.
// No test sends an email or a hit to Google Analytics.
const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '../..');
let browser;
before(async () => { browser = await chromium.launch({ headless: true, ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH } : {}) }); });
after(async () => { await browser?.close(); });

async function fixture(host = 'www.qulacrafts.com') {
  const context = await browser.newContext();
  const blocked = [];
  await context.route('**/*', async route => {
    const url = new URL(route.request().url());
    if (url.hostname !== host || route.request().method() !== 'GET') {
      blocked.push(url.hostname);
      return route.abort();
    }
    const file = path.resolve(root, '.' + (url.pathname === '/' ? '/index.html' : url.pathname));
    if (!file.startsWith(root + path.sep)) return route.abort();
    try { await route.fulfill({ path: file }); } catch { await route.abort(); }
  });
  await context.addInitScript(() => {
    window.__nativePosts = [];
    // Exercise the real submit handler without contacting FormSubmit.
    HTMLFormElement.prototype.submit = function () {
      if (window.__throwSubmit) throw new Error('Simulated browser submit failure');
      window.__nativePosts.push({ action: this.action, fields: [...new FormData(this).entries()].map(([k,v]) => [k, typeof v === 'string' ? v : v.name]) });
    };
  });
  const page = await context.newPage();
  return { context, page, blocked, origin: 'https://' + host };
}
async function fillAndSubmit(page, repeat = 1) {
  return page.evaluate(repeat => {
    const form = document.querySelector('form[action^="https://formsubmit.co/"]');
    for (const field of form.elements) {
      if (field.type === 'hidden' || field.name === '_honey' || field.type === 'file') continue;
      if (field.type === 'email') field.value = 'test@example.com';
      else if (field.type === 'checkbox') field.checked = true;
      else if (field.tagName === 'SELECT' && field.required && !field.value) field.selectedIndex = 1;
      else if (field.required && !field.value) field.value = field.type === 'tel' ? '+12025550123' : 'Test inquiry';
      field.dispatchEvent(new Event('change', { bubbles: true }));
    }
    const valid = form.reportValidity();
    for (let i = 0; i < repeat; i++) form.requestSubmit();
    return valid;
  }, repeat);
}
async function leads(page) {
  return page.evaluate(() => (window.dataLayer || []).filter(e => e[0] === 'event' && e[1] === 'generate_lead').map(e => e[2]));
}

for (const pathname of ['/quote.html','/index.html','/contact.html','/customization.html']) {
  test('preview isolates email and GA4: ' + pathname, async () => {
    const f = await fixture('qula-test.vercel.app');
    try {
      await f.page.goto(f.origin + pathname);
      assert.equal(await fillAndSubmit(f.page), true);
      assert.equal(await f.page.evaluate(() => window.__nativePosts.length), 0);
      assert.equal(f.blocked.includes('formsubmit.co'), false);
      assert.equal(await f.page.evaluate(() => typeof window.gtag), 'undefined');
      assert.match(await f.page.locator('body').innerText(), /Preview validation passed/);
    } finally { await f.context.close(); }
  });
}

test('one production quote submit, confirmation return, and refresh', async () => {
  const f = await fixture();
  try {
    await f.page.goto(f.origin + '/quote.html?sku=YA425&product=Test&category=Acrylic%20Beads');
    assert.equal(await f.page.locator('select[name="product"]').inputValue(), 'Acrylic Beads');
    assert.equal(await fillAndSubmit(f.page, 2), true);
    assert.equal(await f.page.evaluate(() => window.__nativePosts.length), 1);
    assert.equal((await leads(f.page)).length, 0);
    assert.ok(await f.page.evaluate(() => sessionStorage.getItem('qula_pending_inquiry_v1')));
    await f.page.goto(f.origin + '/thank-you.html');
    assert.equal((await leads(f.page)).length, 1);
    assert.equal((await leads(f.page))[0].lead_status, 'confirmed_return');
    await f.page.reload();
    assert.equal((await leads(f.page)).length, 0);
  } finally { await f.context.close(); }
});

test('browser submit failure clears marker and preserves buyer input', async () => {
  const f = await fixture();
  try {
    await f.page.goto(f.origin + '/quote.html');
    await f.page.evaluate(() => { window.__throwSubmit = true; });
    await fillAndSubmit(f.page);
    assert.equal(await f.page.evaluate(() => sessionStorage.getItem('qula_pending_inquiry_v1')), null);
    assert.equal(await f.page.locator('[name="email"]').inputValue(), 'test@example.com');
    assert.match(await f.page.locator('.attachment-status').innerText(), /could not be sent/);
    assert.equal((await leads(f.page)).length, 0);
    await f.page.evaluate(() => { window.__throwSubmit = false; });
    await fillAndSubmit(f.page);
    assert.equal(await f.page.evaluate(() => window.__nativePosts.length), 1);
    // A successful retry can be confirmed normally; an unconfirmed failure cannot.
    await f.page.evaluate(() => window.QULA_CLEAR_INQUIRY_PENDING());
    await f.page.goto(f.origin + '/thank-you.html');
    assert.equal((await leads(f.page)).length, 0);
  } finally { await f.context.close(); }
});

test('attachment rejection does not create a pending lead', async () => {
  const f = await fixture();
  try {
    await f.page.goto(f.origin + '/quote.html');
    await f.page.locator('.file-input-multi').setInputFiles({name:'too-large.png',mimeType:'image/png',buffer:Buffer.alloc(11*1024*1024)});
    await fillAndSubmit(f.page);
    assert.equal(await f.page.evaluate(() => window.__nativePosts.length), 0);
    assert.equal(await f.page.evaluate(() => sessionStorage.getItem('qula_pending_inquiry_v1')), null);
    assert.equal((await leads(f.page)).length, 0);
  } finally { await f.context.close(); }
});

for (const marker of [null, '{bad', JSON.stringify({ts:1}), JSON.stringify({ts:Date.now()+3600000})]) {
  test('direct, invalid, expired or future thank-you marker is not a lead: ' + marker, async () => {
    const f = await fixture();
    try {
      await f.page.goto(f.origin + '/quote.html');
      await f.page.evaluate(marker => { if(marker)sessionStorage.setItem('qula_pending_inquiry_v1',marker); }, marker);
      await f.page.goto(f.origin + '/thank-you.html');
      assert.equal((await leads(f.page)).length, 0);
      assert.equal(await f.page.evaluate(() => sessionStorage.getItem('qula_pending_inquiry_v1')), null);
    } finally { await f.context.close(); }
  });
}

test('cancelled contact submission is not marked as pending', async () => {
  const f = await fixture();
  try {
    await f.page.goto(f.origin + '/contact.html');
    await f.page.evaluate(() => document.querySelector('form').addEventListener('submit', e => e.preventDefault()));
    await fillAndSubmit(f.page);
    assert.equal(await f.page.evaluate(() => sessionStorage.getItem('qula_pending_inquiry_v1')), null);
  } finally { await f.context.close(); }
});
