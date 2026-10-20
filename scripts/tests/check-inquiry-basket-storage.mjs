import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../../assets/js/main.js', import.meta.url), 'utf8');
const start = source.indexOf("  const KEY='qcBasket';");
const end = source.indexOf('  // 浮动篮', start);
assert.ok(start >= 0 && end > start);
function load(raw, unavailable = false) {
  const context = vm.createContext({ localStorage: {
    getItem() { if (unavailable) throw new Error('Storage unavailable'); return raw; },
    setItem() { throw new Error('Reading must not rewrite buyer selections'); }
  } });
  return JSON.parse(JSON.stringify(vm.runInContext(source.slice(start, end) + ';load()', context)));
}
for (const raw of ['{}', 'null', '"text"', '[null]', '[1,true,[],{"sku":null}]', '{']) {
  assert.deepEqual(load(raw), [], raw);
}
assert.deepEqual(load(null), []);
assert.deepEqual(load(null, true), []);
assert.deepEqual(load(JSON.stringify([
  null, { sku: 'MA612', image: '/assets/images/one.webp' },
  { sku: 12 }, { sku: 'MA612', image: '/duplicate.webp' },
  { sku: 'RW20809', image: { toString: null } }, { sku: '' }
])), [
  { sku: 'MA612', image: '/assets/images/one.webp' },
  { sku: 'RW20809', image: '' }
]);
console.log('Inquiry basket storage validation passed: malformed roots, mixed entries, deduplication and unavailable storage.');
