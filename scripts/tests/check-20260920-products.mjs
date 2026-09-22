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

const expectedTitles = new Map([
  ['RW26460', 'Mini Fruit Resin Flatbacks Wholesale | Qula Craft'],
  ['RW26774', 'Christmas Resin Cabochons Wholesale | RW26774'],
  ['RW26775', 'Christmas Cabochon Embellishments Wholesale | RW26775'],
  ['RW26776', 'Christmas Flatback Resin Cabochons Wholesale | RW26776'],
  ['RW26777', 'Christmas Resin Embellishments Wholesale | RW26777'],
  ['RW26796', 'Mixed Christmas Resin Charms Wholesale | RW26796'],
  ['RW26800', 'Mini Gingerbread Resin Figures Wholesale | RW26800'],
  ['RW26813', 'Christmas Resin Miniatures Wholesale | RW26813'],
  ['RW26814', 'Snowy Cottage Resin Miniatures Wholesale | RW26814'],
  ['RW26819', 'Christmas Snowman Tree Resin Cabochons Wholesale | RW26819'],
  ['YX162', 'Candy Cane Polymer Clay Cabochons Wholesale | YX162'],
  ['YX3150', 'Christmas Gingerbread Polymer Clay Slices Wholesale | YX3150'],
  ['YX3461', 'Mixed Christmas Polymer Clay Slices Wholesale | YX3461'],
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
  const title = (page.match(/<title>([\s\S]*?)<\/title>/i) || [])[1] || '';
  if (title !== expectedTitles.get(sku)) throw new Error(`${sku}: unexpected SEO title "${title}"`);
  if (!page.includes('<meta name="robots" content="index,follow">')) throw new Error(`${sku}: PDP is not indexable`);
  const schemas = [...page.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/gi)]
    .map(match => JSON.parse(match[1]));
  const productSchema = schemas.find(item => item['@type'] === 'Product');
  if (!productSchema) throw new Error(`${sku}: Product JSON-LD missing`);
  if (productSchema.sku !== sku || productSchema.url !== `https://www.qulacrafts.com/p-${sku.toLowerCase()}.html`) {
    throw new Error(`${sku}: Product JSON-LD identity mismatch`);
  }
  if (!productSchema.brand || !productSchema.manufacturer || !Array.isArray(productSchema.image) || productSchema.image.length !== 3) {
    throw new Error(`${sku}: Product JSON-LD required fields missing`);
  }
  if (productSchema.offers) throw new Error(`${sku}: quote-only batch must not publish an Offer`);
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
