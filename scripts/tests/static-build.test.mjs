import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const read = name => fs.readFileSync(path.resolve(name), 'utf8');
const pages = fs.readdirSync('.').filter(name => name.endsWith('.html'));
const builtPages = fs.readdirSync('dist').filter(name => name.endsWith('.html'));
const resinPages = ['resin-charms.html', ...builtPages.filter(name => /^resin-charms-page-\d+\.html$/.test(name))
  .sort((a, b) => Number(a.match(/\d+/)[0]) - Number(b.match(/\d+/)[0]))];
const metadata = html => [...html.matchAll(/<script\b[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)].map(m => JSON.parse(m[1]));

test('build preserves every public and archived page, canonical and structured data', () => {
  assert.equal(builtPages.length, pages.length + resinPages.length - 1);
  for (const page of pages) {
    const before = read(page), after = read('dist/' + page);
    const protectedMetadata = html => metadata(html).filter(node => page !== 'resin-charms.html' || node['@type'] !== 'ItemList');
    assert.deepEqual(protectedMetadata(after), protectedMetadata(before), page + ' JSON-LD');
    for (const pattern of [/<link rel="canonical" href="([^"]+)"/, /<meta name="robots" content="([^"]+)"/, /<h1\b[^>]*>([\s\S]*?)<\/h1>/]) {
      const normalize = value => value?.replace(/\s+/g, ' ').trim();
      assert.equal(normalize(after.match(pattern)?.[1]), normalize(before.match(pattern)?.[1]), page + ' protected metadata');
    }
    assert(!/href=["'](?:https:\/\/www\.qulacrafts\.com\/)?\/?quote\.html\?/.test(after), page + ' duplicate inquiry queries');
  }
});

test('all catalog facts and all inquiry parameter values survive the build', () => {
  for (const name of ['product-catalog.json', 'pdp-data.json', 'pdp-copy.json']) {
    const before = JSON.parse(read('assets/data/' + name).replace(/quote\.html\?/g, 'quote.html#rfq:'));
    assert.deepEqual(JSON.parse(read('dist/assets/data/' + name)), before, name);
  }
  for (const page of pages) {
    const before = read(page);
    const after = (page === 'resin-charms.html' ? resinPages : [page]).map(name => read('dist/' + name)).join('');
    for (const [, quote, query] of before.matchAll(/href=(["'])(?:https:\/\/www\.qulacrafts\.com\/)?\/?quote\.html\?([^"']+)\1/g)) {
      const decode = value => value.replace(/&amp;/g, '&').replace(/&#39;/g, "'").replace(/&quot;/g, '"');
      const expected = [...new URLSearchParams(decode(query))];
      const matches = [...after.matchAll(/href=(["'])(?:https:\/\/www\.qulacrafts\.com\/)?\/?quote\.html#rfq:([^"']+)\1/g)];
      assert(matches.some(m => JSON.stringify([...new URLSearchParams(decode(m[2]))]) === JSON.stringify(expected)), page + ' RFQ context');
    }
  }
});

test('consent is present at parse time and all local scripts and styles use built fingerprints', () => {
  for (const page of builtPages) {
    const html = read('dist/' + page);
    assert.equal((html.match(/id="qula-analytics-consent"/g) || []).length, 1, page);
    assert(html.indexOf('id="qula-analytics-consent"') < html.indexOf('<main'), page);
    for (const [, url] of html.matchAll(/(?:src|href)="(\/?assets\/[^"?#]+\.(?:js|css)\?v=[^"]+)"/g)) {
      assert(/\?v=[a-f0-9]{12}$/.test(url), page + ' ' + url);
      assert(fs.existsSync('dist/' + url.replace(/^\//, '').split('?')[0]), url);
    }
  }
  assert(!read('dist/quote.html').includes('hreflang='));
});

test('inquiry-only catalog has no public product prices or historical data backups', () => {
  const data = JSON.parse(read('dist/assets/data/pdp-data.json'));
  for (const entry of data) {
    assert.equal(entry.pricingMode, 'quote_only', entry.assetKey);
    assert.deepEqual(entry.priceTiers, [], entry.assetKey);
    const html = read(`dist/p-${entry.assetKey}.html`);
    assert(!/From\s*\$|itemprop=["'](?:price|lowPrice|highPrice)["']/i.test(html), entry.assetKey);
    const nodes = metadata(html);
    assert(!nodes.some(node => ['Product', 'Offer', 'AggregateOffer'].includes(node['@type'])), entry.assetKey);
  }
  assert(!/ · from \$/i.test(read('dist/llms-full.txt')));
  for (const name of fs.readdirSync('assets/data').filter(name => /\.backup[-.]/.test(name))) {
    assert(!fs.existsSync('dist/assets/data/' + name), name);
    assert(fs.existsSync('assets/data/' + name), name + ' history retained');
  }
});


test('resin pagination keeps each product once with discoverable, self-canonical pages', () => {
  const source = metadata(read('resin-charms.html')).find(node => node['@type'] === 'ItemList');
  const orderedProducts = [];
  const origin = 'https://www.qulacrafts.com/';
  assert.equal(resinPages.length, Math.ceil(source.itemListElement.length / 48));
  for (const [index, name] of resinPages.entries()) {
    const html = read('dist/' + name);
    const items = metadata(html).find(node => node['@type'] === 'ItemList');
    const cards = [...html.matchAll(/<article\b[^>]*class="product-card"[^>]*>[\s\S]*?<h3>\s*<a[^>]+href="([^"]+)"/g)]
      .map(([, url]) => new URL(url, origin).href);
    assert(cards.length > 0 && cards.length <= 48);
    assert.equal(items.numberOfItems, cards.length);
    assert.deepEqual(items.itemListElement.map(item => item.url), cards);
    assert.equal(html.match(/rel="canonical" href="([^"]+)"/)?.[1], origin + name);
    if (index + 1 < resinPages.length) assert(html.includes(`href="${resinPages[index + 1]}" rel="next"`));
    if (index > 0) assert(html.includes(`href="${resinPages[index - 1]}" rel="prev"`));
    orderedProducts.push(...cards);
  }
  assert.equal(new Set(orderedProducts).size, orderedProducts.length);
  assert.deepEqual(orderedProducts, source.itemListElement.map(item => item.url));
});
