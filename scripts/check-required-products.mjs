#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MIN_PRODUCT_COUNT = 176;
const REQUIRED = [
  { sku: 'RW967', key: 'rw967' },
  { sku: 'RW474', key: 'rw474' },
  { sku: 'RW326', key: 'rw326' },
  { sku: 'RW26740', key: 'rw26740' },
];

function fail(message) {
  console.error(`Protected product check failed: ${message}`);
  process.exitCode = 1;
}

function verifyCategoryHtml(content, label) {
  for (const { sku, key } of REQUIRED) {
    if (!content.includes(`data-sku="${sku}"`)) fail(`${label} has no ${sku} product card`);
    if (!content.includes(`href="p-${key}.html"`)) fail(`${label} has no ${sku} PDP link`);
    if (!content.includes(`assets/images/pdp/${key}/01.webp`)) fail(`${label} has no ${sku} product image`);
  }
}

const liveIndex = process.argv.indexOf('--live');
if (liveIndex !== -1) {
  const liveFile = process.argv[liveIndex + 1];
  if (!liveFile || !fs.existsSync(liveFile)) {
    fail('live category snapshot is missing');
  } else {
    verifyCategoryHtml(fs.readFileSync(liveFile, 'utf8'), 'production resin category');
  }
} else {
  const catalog = JSON.parse(fs.readFileSync(path.join(ROOT, 'assets/data/product-catalog.json'), 'utf8'));
  const pdpData = JSON.parse(fs.readFileSync(path.join(ROOT, 'assets/data/pdp-data.json'), 'utf8'));
  const products = catalog.categories.flatMap(category => category.products || []);
  if (products.length < MIN_PRODUCT_COUNT) fail(`catalog has ${products.length} products; expected at least ${MIN_PRODUCT_COUNT}`);
  if (pdpData.length < MIN_PRODUCT_COUNT) fail(`PDP data has ${pdpData.length} records; expected at least ${MIN_PRODUCT_COUNT}`);

  for (const { sku, key } of REQUIRED) {
    const catalogRow = products.find(product => product.sku === sku && product.pdp === `p-${key}.html`);
    const pdpRow = pdpData.find(product => product.sku === sku && product.assetKey === key);
    if (!catalogRow) fail(`catalog is missing ${sku}`);
    if (!pdpRow) fail(`PDP data is missing ${sku}`);
    for (const file of [`p-${key}.html`, `assets/images/pdp/${key}/01.webp`, `assets/images/pdp/${key}/02.webp`, `assets/images/pdp/${key}/03.webp`]) {
      if (!fs.existsSync(path.join(ROOT, file))) fail(`${sku} is missing ${file}`);
    }
  }
  verifyCategoryHtml(fs.readFileSync(path.join(ROOT, 'resin-charms.html'), 'utf8'), 'repository resin category');
}

if (!process.exitCode) {
  console.log(`Protected product check passed: ${REQUIRED.map(product => product.sku).join(', ')} are present.`);
}
