#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MIN_PRODUCT_COUNT = 218;
const REQUIRED = [
  { sku: 'RW967', key: 'rw967' },
  { sku: 'RW474', key: 'rw474' },
  { sku: 'RW326', key: 'rw326' },
  { sku: 'RW26740', key: 'rw26740' },
  { sku: 'RW26746', key: 'rw26746' },
  { sku: 'RW26768', key: 'rw26768' },
  { sku: 'RW370', key: 'rw370' },
  { sku: 'RW927', key: 'rw927' },
  { sku: 'RW001078', key: 'rw001078' },
  { sku: 'RW1394', key: 'rw1394' },
  { sku: 'RW2445', key: 'rw2445' },
  { sku: 'RW22405', key: 'rw22405' },
  { sku: 'RW26637', key: 'rw26637' },
  { sku: 'RW26692', key: 'rw26692' },
  { sku: 'YX002', key: 'yx002', categoryFile: 'polymer-clay-sprinkles.html' },
  { sku: 'YX004', key: 'yx004', categoryFile: 'polymer-clay-sprinkles.html' },
  { sku: 'YX051', key: 'yx051', categoryFile: 'polymer-clay-sprinkles.html' },
  { sku: 'YX4138', key: 'yx4138', categoryFile: 'polymer-clay-sprinkles.html' },
];

function fail(message) {
  console.error(`Protected product check failed: ${message}`);
  process.exitCode = 1;
}

function verifyCategoryHtml(content, label, categoryFile = 'resin-charms.html') {
  for (const { sku, key, categoryFile: requiredCategory = 'resin-charms.html' } of REQUIRED) {
    if (requiredCategory !== categoryFile) continue;
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
  verifyCategoryHtml(
    fs.readFileSync(path.join(ROOT, 'polymer-clay-sprinkles.html'), 'utf8'),
    'repository polymer clay category',
    'polymer-clay-sprinkles.html',
  );
}

if (!process.exitCode) {
  console.log(`Protected product check passed: ${REQUIRED.map(product => product.sku).join(', ')} are present.`);
}
