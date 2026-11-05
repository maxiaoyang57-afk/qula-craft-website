import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = async name => JSON.parse(await fs.readFile(path.join(root, 'assets/data', name), 'utf8'));
const [selection, catalog, products, verified] = await Promise.all([
  read('seasonal-collections.json'), read('product-catalog.json'), read('pdp-data.json'), read('verified-product-specs.json'),
]);
const esc = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const byPage = new Map(catalog.categories.flatMap(category => category.products.map(product => [product.pdp, { product, category }])));
const factsByPage = new Map(products.map(product => ['p-' + product.assetKey + '.html', product]));
const categoryLabels = {
  'slime-charms': 'Slime Charms', 'polymer-clay-slices': 'Polymer Clay Sprinkles',
  'plastic-sequins': 'Glitter & Fillers', 'resin-charms': 'Resin Charms',
  'pvc-plastic-charms': 'PVC Plastic Charms', 'plastic-beads': 'Acrylic Beads',
  'beads-for-pens': 'Beads for Pens', keychain: 'Keychains', 'jewelry-accessories': 'Jewelry Accessories',
};

// Preserve all size qualifications. A bag weight filed under Size is a pack,
// never an item dimension; MOQ, prices and title fragments are not pack sources.
function cardFacts(product) {
  const specs = { ...product.specs, ...verified[product.sku] };
  const size = ['Size', 'Dimensions', 'Reference size', 'Size reference']
    .map(key => specs[key]).find(value => typeof value === 'string' && /[1-9]\d*(?:\.\d+)?\s*(?:mm|cm)\b/i.test(value));
  const normalize = value => value.replace(/(?<=\d)\s*[x×*]\s*(?=\d)/gi, ' × ')
    .replace(/(\d)(mm|cm)\b/gi, '$1 $2').trim();
  const entries = size ? [['Size', normalize(size)]] : [];
  const packPattern = /\d[\d,.]*\s*(?:pcs?|pieces?|sets?|g|kg)\s*(?:\/|per\s+)\s*(?:bag|pack|sleeve|batch|set)\b/i;
  let pack = ['Source packing', 'Standard pack', 'Pack reference', 'Packaging', 'Size']
    .map(key => ({ key, value: specs[key] })).find(({ value }) => typeof value === 'string' && packPattern.test(value));
  if (!pack && typeof specs['Reference specification'] === 'string') {
    const match = specs['Reference specification'].match(/^Reference pack:\s*(\d[\d,.]*\s*(?:g|kg|pcs?|pieces?|sets?))(?=;|$)/i);
    if (match) pack = { key: 'Pack reference', value: match[1] };
  }
  if (pack) {
    const value = pack.value.replace(/; custom packing by inquiry$/i, '')
      .replace(/\s*\(live official product attribute,[^)]*\)$/i, '').trim();
    entries.push(['Reference pack', value]);
  }
  return entries;
}

const selected = [], seen = new Set();
if (selection.groups.length !== 5 || selection.featuredPerSeason !== 4) throw Error('Unexpected seasonal layout configuration');
const counts = new Map();
function card(pdp, group) {
  if (seen.has(pdp)) throw Error('Duplicate seasonal PDP: ' + pdp);
  seen.add(pdp);
  const source = byPage.get(pdp), facts = factsByPage.get(pdp);
  if (!source || !facts || source.product.sku !== facts.sku) throw Error('Missing or mismatched public product: ' + pdp);
  const { product, category } = source;
  if (!categoryLabels[category.slug]) throw Error('Unknown category: ' + category.slug);
  awaitableFiles.push(pdp, product.image);
  const specs = cardFacts(facts), title = product.titleFull || product.title;
  selected.push({ sku: product.sku, pdp, title, category: category.slug, categoryLabel: categoryLabels[category.slug], image: product.image, group: group.key, specs });
  const params = new URLSearchParams({ sku: product.sku, product: title, category: categoryLabels[category.slug], image: product.image, source: 'seasonal-collections', entry_page: '/seasonal-collections.html', entry_context: 'product' });
  const wa = 'https://wa.me/8618632026595?text=' + encodeURIComponent('Hello Qula Craft, I am interested in SKU ' + product.sku + '. Please help me with product details and a quotation.');
  return '<article class="product-card" data-seasonal-sku="' + esc(product.sku) + '"><div class="product-img"><a href="' + esc(pdp) + '"><img loading="lazy" src="' + esc(product.image) + '" alt="' + esc(product.imageAlt || product.sku + ' ' + title) + '" width="' + product.imageWidth + '" height="' + product.imageHeight + '"></a></div><div class="product-info"><span class="pill">' + esc(group.label) + '</span><span class="seasonal-sku">SKU ' + esc(product.sku) + '</span><h3><a href="' + esc(pdp) + '">' + esc(title) + '</a></h3>' +
    (specs.length ? '<dl class="seasonal-card-specs">' + specs.map(([label, value]) => '<div><dt>' + label + '</dt><dd>' + esc(value) + '</dd></div>').join('') + '</dl>' : '') +
    '<div class="seasonal-card-actions"><a class="btn seasonal-details" href="' + esc(pdp) + '">View product details →</a><a class="btn btn-card" href="' + esc('quote.html?' + params) + '">Ask about ' + esc(product.sku) + ' →</a></div><a class="wa-line" href="' + esc(wa) + '" target="_blank" rel="noopener noreferrer">or Chat on WhatsApp ›</a></div></article>';
}
const awaitableFiles = [];
let collection = '<section class="section seasonal-catalog" id="seasonal-products" aria-label="Seasonal product catalog"><div class="container">';
for (const group of selection.groups) {
  if (group.products.length !== 12) throw Error('Expected 12 selected products for ' + group.key);
  counts.set(group.key, group.products.length);
  const cards = group.products.map(pdp => card(pdp, group));
  collection += '<div class="seasonal-product-group" id="' + group.id + '"><div class="section-head"><span class="eyebrow">' + cards.length + ' catalog designs</span><h2>' + esc(group.label) + ' craft supplies</h2><p>Open a product page for details, or use its SKU to ask about quantities, packing and availability. Pack references are not minimum order quantities.</p></div><div class="product-grid compact">' + cards.slice(0, 4).join('') + '</div><details class="seasonal-more"><summary>View ' + (cards.length - 4) + ' more ' + esc(group.label) + ' products</summary><div class="product-grid compact">' + cards.slice(4).join('') + '</div></details>';
  if (group.key === 'Christmas') collection += '<p><a class="seasonal-guide-link" href="blog-christmas-gifts-for-family-diy.html">See family Christmas DIY gift ideas →</a></p>';
  collection += '</div>';
}
collection += '</div></section>';
for (const file of awaitableFiles) await fs.access(path.join(root, file));
const nav = '<nav class="seasonal-quicklinks" aria-label="Browse seasonal products">' + selection.groups.map(group => '<a href="#' + group.id + '">' + esc(group.label) + ' products <span>' + counts.get(group.key) + '</span></a>').join('') + '</nav>';
const page = path.join(root, 'seasonal-collections.html'), before = await fs.readFile(page, 'utf8');
const navPattern = /<nav class="seasonal-quicklinks"[^>]*>[\s\S]*?<\/nav>/g;
const sectionPattern = /<section class="section seasonal-catalog"[^>]*>[\s\S]*?<\/section>/g;
if ([...before.matchAll(navPattern)].length !== 1 || [...before.matchAll(sectionPattern)].length !== 1) throw Error('Expected one seasonal navigation and product section');
const after = before.replace(navPattern, () => nav).replace(sectionPattern, () => collection);
if (process.argv.includes('--write')) await fs.writeFile(page, after);
else if (after !== before) throw Error('Seasonal selection/specifications are out of date. Run node scripts/sync-seasonal-collections.mjs --write, then review the page.');
const summary = { products: selected.length, groups: Object.fromEntries(counts), withSize: selected.filter(p => p.specs.some(([key]) => key === 'Size')).length, withPack: selected.filter(p => p.specs.some(([key]) => key === 'Reference pack')).length };
if (process.argv.includes('--audit')) console.log(JSON.stringify({ summary, selected }, null, 2));
else console.log('Seasonal catalog sources and specifications verified: ' + JSON.stringify(summary));
