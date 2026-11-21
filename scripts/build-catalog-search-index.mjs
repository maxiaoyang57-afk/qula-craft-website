import { readFile, writeFile } from 'node:fs/promises';

// Only index specifications attached to currently published catalog products.
const catalog = JSON.parse(await readFile('assets/data/product-catalog.json', 'utf8'));
const details = JSON.parse(await readFile('assets/data/pdp-data.json', 'utf8'));
const byKey = new Map(details.map(p => [p.assetKey, p]));
const index = {};
for (const group of catalog.categories || []) {
  for (const product of group.products || []) {
    const key = (product.pdp || '').match(/^p-(.+)\.html$/)?.[1];
    const detail = byKey.get(key);
    if (!detail || detail.sku !== product.sku) continue;
    const specs = detail.specs || {};
    const words = Object.entries(specs)
      .filter(([name, value]) => /^(material|loose beads material|application|usage|size|hole|hole diameter|shape)$/i.test(name) && typeof value === 'string')
      .map(([, value]) => value.trim())
      .filter(value => value && !/^(other|n\/?a|unknown|none)$/i.test(value));
    if (words.length) index[product.pdp] = words.join(' ');
  }
}
await writeFile('assets/data/catalog-search-specs.json', JSON.stringify(index));
console.log(`Search specifications indexed for ${Object.keys(index).length} catalog products`);

