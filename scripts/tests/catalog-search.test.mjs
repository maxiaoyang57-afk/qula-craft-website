import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { setImmediate } from 'node:timers/promises';
import test from 'node:test';
import vm from 'node:vm';

const source = readFileSync(new URL('../../assets/js/main.js', import.meta.url), 'utf8');
const start = source.indexOf('// products hub ');
const end = source.indexOf('// 询盘篮 Quote Basket', start);
assert.ok(start >= 0 && end > start, 'Run the real catalog-search initializer');
const searchSource = source.slice(start, end);
const product = (sku, title) => ({ sku, title, category: 'Resin Charms', image: '/assets/test.jpg',
  imageAlt: title, imageWidth: 1000, imageHeight: 1000, pdp: 'p-' + sku.toLowerCase() + '.html' });
const catalog = { categories: [{ products: [product('RW26808', 'First resin product'),
  product('RW20809', 'Second resin product'), product('RW337/285', 'Grouped resin products')] }] };

function fixture(search = '') {
  const listeners = new Map(), timers = new Map(), requests = [];
  let timerId = 0;
  const input = { value: '', addEventListener: (name, fn) => listeners.set(name, fn) };
  const results = { hidden: true, innerHTML: '' }, count = { textContent: '' }, grid = { style: { display: '' } };
  vm.runInNewContext(searchSource, {
    URLSearchParams, location: { search },
    document: { querySelector: selector => ({ '[data-catalog-search]': input,
      '[data-search-results]': results, '[data-search-count]': count, '.category-grid': grid }[selector] || null) },
    fetch: () => new Promise((resolve, reject) => requests.push({
      resolve: (data = catalog, ok = true) => resolve({ ok, json: async () => data }), reject,
    })),
    setTimeout: fn => { timers.set(++timerId, fn); return timerId; },
    clearTimeout: id => timers.delete(id),
  });
  return {
    input, results, count, grid, requests,
    type(value) { input.value = value; listeners.get('input')(); },
    async debounce() { const callbacks = [...timers.values()]; timers.clear(); callbacks.forEach(fn => fn()); await setImmediate(); },
    async settle() { await setImmediate(); },
  };
}

test('clearing a query while the catalog loads keeps categories visible after the old response', async () => {
  const f = fixture();
  f.type('RW26808'); await f.debounce();
  assert.equal(f.requests.length, 1);
  f.type(''); await f.debounce();
  f.requests[0].resolve(); await f.settle();
  assert.equal(f.results.hidden, true);
  assert.equal(f.results.innerHTML, '');
  assert.equal(f.count.textContent, '');
  assert.equal(f.grid.style.display, '');
});

test('editing a pending query invalidates its result before the next debounce runs', async () => {
  const f = fixture();
  f.type('RW26808'); await f.debounce();
  f.type('RW20809');
  f.requests[0].resolve(); await f.settle();
  assert.equal(f.results.hidden, true, 'The old SKU must not appear for the new input');
  assert.doesNotMatch(f.results.innerHTML, /RW26808/);
  await f.debounce();
  assert.match(f.results.innerHTML, /RW20809/);
  assert.doesNotMatch(f.results.innerHTML, /RW26808/);
});

test('overlapping searches share the pending catalog request and only the latest query renders', async () => {
  const f = fixture();
  f.type('RW26808'); await f.debounce();
  f.type('RW20809'); await f.debounce();
  const count = f.requests.length;
  f.requests.forEach(request => request.resolve()); await f.settle();
  assert.equal(count, 1, 'Only one catalog download is needed');
  assert.match(f.results.innerHTML, /RW20809/);
  assert.doesNotMatch(f.results.innerHTML, /RW26808/);
  assert.equal(f.results.hidden, false);
});

test('clearing cached results restores the category grid immediately', async () => {
  const f = fixture();
  f.type('RW26808'); await f.debounce();
  f.requests[0].resolve(); await f.settle();
  assert.equal(f.results.hidden, false);
  f.type('');
  assert.equal(f.results.hidden, true);
  assert.equal(f.grid.style.display, '');
  assert.equal(f.results.innerHTML, '');
});

test('a failed catalog request leaves categories available and a later search can retry', async () => {
  const f = fixture();
  f.type('RW26808'); await f.debounce();
  f.requests[0].reject(new Error('Synthetic network failure')); await f.settle();
  assert.equal(f.results.hidden, true);
  assert.equal(f.grid.style.display, '');
  assert.match(f.count.textContent, /temporarily unavailable/i);
  f.type('RW20809'); await f.debounce();
  assert.equal(f.requests.length, 2);
  f.requests[1].resolve(); await f.settle();
  assert.match(f.results.innerHTML, /RW20809/);
  assert.doesNotMatch(f.count.textContent, /unavailable/i);
});

test('a stale HTTP failure cannot replace the cleared-query state', async () => {
  const f = fixture();
  f.type('RW26808'); await f.debounce();
  f.type(''); await f.debounce();
  f.requests[0].resolve({ categories: [] }, false); await f.settle();
  assert.equal(f.count.textContent, '');
  assert.equal(f.results.hidden, true);
});

test('URL searches, shorthand group codes and subsequent cached searches keep exact SKU matching', async () => {
  const f = fixture('?search=RW20809');
  assert.equal(f.input.value, 'RW20809');
  assert.equal(f.requests.length, 1);
  f.requests[0].resolve(); await f.settle();
  assert.match(f.results.innerHTML, /RW20809/);
  f.type('rw285'); await f.debounce();
  assert.match(f.results.innerHTML, /RW337\/285/);
  assert.doesNotMatch(f.results.innerHTML, /RW20809/);
  assert.equal(f.requests.length, 1);
});
