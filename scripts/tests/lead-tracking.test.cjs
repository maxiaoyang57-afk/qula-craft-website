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

async function buyingClicks(page) {
  return page.evaluate(() => (window.dataLayer || []).filter(e => e[0] === 'event' && ['product_click','quote_click'].includes(e[1])).map(e => ({name:e[1],params:e[2]})));
}
async function preventTestNavigation(page) {
  // Registered after analytics: exercise real DOM bubbling without leaving the
  // page, and keep every network request in the local fixture.
  await page.evaluate(() => document.addEventListener('click', e => {
    if(e.target.closest?.('a'))e.preventDefault();
  }));
}

test('guide product and quote clicks are consented, once, and contain no inquiry query', async () => {
  const f = await fixture();
  try {
    await f.page.goto(f.origin + '/guide-slime-business-supply-checklist.html?email=buyer%40example.com');
    await preventTestNavigation(f.page);
    await f.page.locator('a[href="p-yx043.html"]').first().click();
    assert.equal((await buyingClicks(f.page)).length,0);
    await f.page.locator('[data-analytics-accept]').click();
    await f.page.locator('a[href="p-yx043.html"]').first().click();
    // Dynamic, nested search/card links work without registering new handlers.
    await f.page.evaluate(() => {
      const card=document.createElement('div');card.className='product-card';
      card.innerHTML='<a href="/quote.html?sku=YX043&product=buyer%40example.com#private"><span id="test-quote-child">Ask us</span></a>';
      document.querySelector('main').appendChild(card);
    });
    await f.page.locator('#test-quote-child').click();
    await f.page.locator('.mobile-cta-bar a[href*="quote.html"]').first().evaluate(a=>a.click());
    const events=await buyingClicks(f.page);
    assert.deepEqual(events.map(e=>e.name),['product_click','quote_click','quote_click']);
    assert.equal(events[0].params.destination_path,'/p-yx043.html');
    assert.equal(events[1].params.destination_path,'/quote.html');
    assert.equal(events[1].params.link_location,'product_card');
    assert.equal(events[2].params.link_location,'mobile_cta');
    for(const e of events){
      assert.deepEqual(Object.keys(e.params).sort(),['destination_path','link_location','page_location','page_path']);
      assert.equal(e.params.page_path,'/guide-slime-business-supply-checklist.html');
      assert.equal(e.params.page_location,f.origin+'/guide-slime-business-supply-checklist.html');
      assert.doesNotMatch(JSON.stringify(e),/@|%40|email=|sku=|#private/);
    }
    assert.equal((await leads(f.page)).length,0);
    await f.page.locator('.qc-cookie-settings').click();
    await f.page.locator('[data-analytics-decline]').click();
    await f.page.locator('a[href="p-yx043.html"]').first().click();
    assert.equal((await buyingClicks(f.page)).length,3);
  } finally { await f.context.close(); }
});

test('external lookalikes and non-buying links are not buying clicks', async () => {
  const f=await fixture();
  try {
    await f.page.goto(f.origin+'/resin-charms.html');
    await f.page.locator('[data-analytics-accept]').click();
    await preventTestNavigation(f.page);
    await f.page.evaluate(() => {
      for(const href of ['https://qulacrafts.com.evil.example/p-yx043.html','https://user:secret@www.qulacrafts.com/quote.html','https://www.qulacrafts.com:8443/quote.html','/products.html','/quote.html/extra','mailto:sales@qulacrafts.com','#quote']){
        const a=document.createElement('a');a.href=href;a.textContent='Test';document.body.appendChild(a);a.click();a.remove();
      }
    });
    assert.equal((await buyingClicks(f.page)).length,0);
  } finally { await f.context.close(); }
});

for(const privacy of [{globalPrivacyControl:true},{doNotTrack:'1'}]){
  test('privacy signal suppresses new buying clicks: '+JSON.stringify(privacy), async()=>{
    const f=await fixture();
    try {
      await f.context.addInitScript(privacy=>{
        for(const [key,value] of Object.entries(privacy))Object.defineProperty(navigator,key,{get:()=>value,configurable:true});
        localStorage.setItem('qula_analytics_consent_v1','granted');
      },privacy);
      await f.page.goto(f.origin+'/guide-bingsu-beads-slime-fillers.html');
      await preventTestNavigation(f.page);
      await f.page.locator('a[href="p-ym109.html"]').first().click();
      assert.equal((await buyingClicks(f.page)).length,0);
    } finally {await f.context.close();}
  });
}

for (const entryPage of ['/\\[', '/\\outside.example/path', '/p-ya893.html?ref=guide#details']) {
  test('quote source URL stays local and preserves preview guards: ' + entryPage, async () => {
    const f = await fixture('qula-test.vercel.app');
    const errors = [];
    f.page.on('pageerror', error => errors.push(error.message));
    try {
      const params = new URLSearchParams({ sku: 'YA893', product: 'Test product', entry_page: entryPage });
      const quoteUrl = f.origin + '/quote.html?' + params;
      await f.page.goto(quoteUrl);
      assert.deepEqual(errors, []);
      assert.equal(await f.page.locator('#inquiryForm').evaluate(form => typeof form.onsubmit), 'function');
      const expected = entryPage.startsWith('/p-') ? 'https://www.qulacrafts.com' + entryPage : quoteUrl;
      assert.equal(await f.page.locator('#hiddenUrl').inputValue(), expected);
      assert.equal(await fillAndSubmit(f.page), true);
      assert.equal(await f.page.evaluate(() => window.__nativePosts.length), 0);
      assert.equal(f.blocked.includes('formsubmit.co'), false);
      assert.equal((await leads(f.page)).length, 0);
      assert.match(await f.page.locator('body').innerText(), /Preview validation passed/);
    } finally { await f.context.close(); }
  });
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

test('a rejected attachment is not a lead and does not prevent a later explicit inquiry', async () => {
  const f = await fixture();
  try {
    await f.page.goto(f.origin + '/quote.html');
    await f.page.locator('.file-input-multi').setInputFiles({name:'too-large.png',mimeType:'image/png',buffer:Buffer.alloc(11*1024*1024)});
    assert.equal(await f.page.locator('.file-list .file-item').count(), 0);
    assert.equal(await f.page.evaluate(() => window.__nativePosts.length), 0);
    assert.equal(await f.page.evaluate(() => sessionStorage.getItem('qula_pending_inquiry_v1')), null);
    assert.equal((await leads(f.page)).length, 0);
    await fillAndSubmit(f.page);
    assert.equal(await f.page.evaluate(() => window.__nativePosts.length), 1);
    assert.equal(await f.page.locator('[data-native-attachment]').count(), 0);
    assert.notEqual(await f.page.evaluate(() => sessionStorage.getItem('qula_pending_inquiry_v1')), null);
    assert.equal((await leads(f.page)).length, 0);
    assert.equal(f.blocked.includes('formsubmit.co'), false);
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
