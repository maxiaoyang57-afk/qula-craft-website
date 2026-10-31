import fs from 'node:fs';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const policy = JSON.parse(read('scripts/data/catalog-scope-20261031.json'));
const catalog = JSON.parse(read('assets/data/product-catalog.json'));
assert.deepEqual(catalog.categories.map(c => c.slug), policy.activeCategories, 'Only the original nine categories may be public');
const active = catalog.categories.flatMap(c => c.products);
const archived = catalog.archivedProducts || [];
assert.equal(catalog.totalProducts, active.length);
assert.deepEqual(archived.map(p => p.sku).sort(), policy.products.map(p => p.sku).sort());
const sitemap = read('sitemap.xml');
for (const source of policy.products) {
  assert.equal(active.some(p => p.sku === source.sku), false, `${source.sku} must not return to public browsing`);
  const item = archived.find(p => p.sku === source.sku);
  assert.equal(item.pdp, source.pdp);
  assert.equal(item.image, source.image);
  const page = read(item.pdp);
  assert.match(page, /data-catalog-archive/);
  assert.match(page, /<meta name="robots" content="noindex,follow">/);
  const schemas = [...page.matchAll(/<script type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/g)].map(m => JSON.parse(m[1]));
  assert.ok(schemas.some(node => node['@type'] === 'Product' && node.sku === source.sku), 'Original Product identity remains available');
  assert.ok(page.includes(source.image), 'Original catalog photo remains available');
  assert.ok(!sitemap.includes(`<loc>https://www.qulacrafts.com/${item.pdp}</loc>`));
  assert.ok(!read('llms-full.txt').includes(`](https://www.qulacrafts.com/${item.pdp})`));
}
for (const name of ['index.html', 'products.html', 'quote.html']) {
  assert.ok(!read(name).includes('Decorative Craft Accessories'), `${name}: retired category entry remains`);
}
assert.ok(!sitemap.includes('<loc>https://www.qulacrafts.com/decorative-craft-accessories.html</loc>'));
console.log(`Fixed category scope passed: 9 categories, ${active.length} public products, ${archived.length} preserved references.`);
