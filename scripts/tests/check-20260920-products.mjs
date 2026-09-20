import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'assets/data/product-catalog.json'), 'utf8'));
const pdp = JSON.parse(fs.readFileSync(path.join(root, 'assets/data/pdp-data.json'), 'utf8'));
const products = catalog.categories.flatMap(category => category.products || []);
const expected = new Map([
  ['RW26460', 'resin-charms'], ['RW26774', 'resin-charms'], ['RW26775', 'resin-charms'],
  ['RW26776', 'resin-charms'], ['RW26777', 'resin-charms'], ['RW26796', 'resin-charms'],
  ['RW26800', 'resin-charms'], ['RW26813', 'resin-charms'], ['RW26814', 'resin-charms'],
  ['RW26819', 'resin-charms'], ['YX162', 'polymer-clay-slices'],
  ['YX3150', 'polymer-clay-slices'], ['YX3461', 'polymer-clay-slices'],
]);

for (const [sku, categorySlug] of expected) {
  const catalogRows = products.filter(row => row.sku === sku);
  const pdpRows = pdp.filter(row => row.sku === sku);
  if (catalogRows.length !== 1 || pdpRows.length !== 1) throw new Error(`${sku}: expected one catalog and one PDP record`);
  if (catalogRows[0].categorySlug !== categorySlug || pdpRows[0].categorySlug !== categorySlug) throw new Error(`${sku}: category mismatch`);
  if (pdpRows[0].imagesLocal.length !== 3) throw new Error(`${sku}: expected three gallery images`);
  for (const image of pdpRows[0].imagesLocal) {
    if (!fs.existsSync(path.join(root, image))) throw new Error(`${sku}: missing ${image}`);
  }
  const pagePath = path.join(root, `p-${sku.toLowerCase()}.html`);
  const page = fs.readFileSync(pagePath, 'utf8');
  if (!page.includes(`SKU ${sku}`) || !page.includes(`p-${sku.toLowerCase()}.html`)) throw new Error(`${sku}: PDP identity or canonical missing`);
  for (const image of pdpRows[0].imagesLocal) {
    if (!page.includes(image)) throw new Error(`${sku}: PDP does not reference ${image}`);
  }
}

for (const category of [
  ['resin-charms.html', [...expected].filter(([, slug]) => slug === 'resin-charms').map(([sku]) => sku)],
  ['polymer-clay-sprinkles.html', [...expected].filter(([, slug]) => slug === 'polymer-clay-slices').map(([sku]) => sku)],
]) {
  const page = fs.readFileSync(path.join(root, category[0]), 'utf8');
  for (const sku of category[1]) {
    if (!page.includes(`data-sku="${sku}"`) || !page.includes(`p-${sku.toLowerCase()}.html`)) throw new Error(`${sku}: category card missing`);
  }
}

for (const sku of expected.keys()) {
  if (!fs.readFileSync(path.join(root, 'sitemap.xml'), 'utf8').includes(`p-${sku.toLowerCase()}.html`)) throw new Error(`${sku}: sitemap entry missing`);
}

if (products.filter(row => row.sku === 'RW002155').length !== 1 || pdp.filter(row => row.sku === 'RW002155').length !== 1) {
  throw new Error('RW002155 duplicate protection failed');
}

console.log(`2026-09-20 QULA batch check passed: ${expected.size} new SKUs and RW002155 unchanged.`);
