import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const files = fs.readdirSync(root).filter((name) => name.endsWith('.html')).sort();
const base = 'https://www.qulacrafts.com/';
const failures = [];
const titles = new Map();
const descriptions = new Map();
const canonicals = new Map();

function decode(value) {
  return value
    .replace(/&amp;/g, '&')
    .replace(/&#8211;|&ndash;/g, '–')
    .replace(/&#8212;|&mdash;/g, '—')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/<[^>]+>/g, '')
    .trim();
}

function add(map, key, file) {
  if (!key) return;
  const list = map.get(key) || [];
  list.push(file);
  map.set(key, list);
}

const indexable = [];
for (const file of files) {
  const html = fs.readFileSync(path.join(root, file), 'utf8');
  const noindex = /<meta[^>]+name="robots"[^>]+noindex/i.test(html);
  const title = decode((html.match(/<title>([\s\S]*?)<\/title>/i) || [])[1] || '');
  const description = decode((html.match(/<meta\s+name="description"\s+content="([^"]*)"/i) || [])[1] || '');
  const canonical = (html.match(/<link\s+rel="canonical"\s+href="([^"]*)"/i) || [])[1] || '';
  const h1Count = (html.match(/<h1\b/gi) || []).length;
  const quoteOnly = /<b>Quoted by pack and quantity<\/b>/i.test(html);

  if (!title) failures.push(`${file}: missing title`);
  if (h1Count !== 1) failures.push(`${file}: expected one H1, found ${h1Count}`);
  if (/quantitys\b|\bbagss\b/i.test(html)) failures.push(`${file}: malformed pricing copy`);

  for (const raw of html.matchAll(/<script\s+type="application\/ld\+json">([\s\S]*?)<\/script>/gi)) {
    try {
      const data = JSON.parse(raw[1]);
      if (quoteOnly && data['@type'] === 'Product' && data.offers) {
        failures.push(`${file}: quote-only product must not publish an Offer`);
      }
    } catch (error) {
      failures.push(`${file}: invalid JSON-LD (${error.message})`);
    }
  }

  for (const img of html.match(/<img\b[^>]*>/gi) || []) {
    // Empty-src elements are hidden client-side placeholders, not crawlable images.
    if (/\bsrc=""/i.test(img)) continue;
    if (!/\balt="[^"]*"/i.test(img)) failures.push(`${file}: image missing alt attribute`);
    if (!/\bwidth="\d+"/i.test(img) || !/\bheight="\d+"/i.test(img)) {
      failures.push(`${file}: image missing numeric width/height`);
    }
  }

  if (noindex) continue;
  indexable.push(file);
  const expected = file === 'index.html' ? base : base + file;
  if (!description) failures.push(`${file}: missing meta description`);
  if (title.length > 65) failures.push(`${file}: title is ${title.length} characters`);
  if (description.length < 80 || description.length > 160) {
    failures.push(`${file}: description is ${description.length} characters`);
  }
  if (canonical !== expected) failures.push(`${file}: canonical should be ${expected}`);
  add(titles, title, file);
  add(descriptions, description, file);
  add(canonicals, canonical, file);

  const price = html.match(/<b>From \$[^<]+ \/ ([^<]+)<\/b> · MOQ ([^—<]+)/i);
  if (price) {
    const family = (text) => /\b(?:bag|bags|box|boxes|set|sets|roll|rolls)\b/i.test(text)
      ? 'pack'
      : /\b(?:pc|pcs|piece|pieces|pair|pairs)\b/i.test(text) ? 'piece' : null;
    if (family(price[1]) && family(price[2]) && family(price[1]) !== family(price[2])) {
      failures.push(`${file}: price unit ${price[1]} conflicts with MOQ ${price[2].trim()}`);
    }
  }
}

for (const [label, map] of [['title', titles], ['description', descriptions], ['canonical', canonicals]]) {
  for (const [value, owners] of map) {
    if (owners.length > 1) failures.push(`duplicate ${label}: ${owners.join(', ')} (${value.slice(0, 80)})`);
  }
}

const sitemap = fs.readFileSync(path.join(root, 'sitemap.xml'), 'utf8');
const sitemapUrls = [...sitemap.matchAll(/<loc>(https:\/\/www\.qulacrafts\.com\/[^<]*)<\/loc>/g)]
  .map((match) => match[1])
  .filter((url) => !url.includes('/assets/'));
const expectedUrls = new Set(indexable.map((file) => file === 'index.html' ? base : base + file));
const actualUrls = new Set(sitemapUrls);
for (const url of expectedUrls) if (!actualUrls.has(url)) failures.push(`sitemap missing ${url}`);
for (const url of actualUrls) if (!expectedUrls.has(url)) failures.push(`sitemap includes non-indexable ${url}`);

const vercel = JSON.parse(fs.readFileSync(path.join(root, 'vercel.json'), 'utf8'));
const hasCanonicalRedirect = (vercel.redirects || []).some((rule) =>
  rule.destination === 'https://www.qulacrafts.com/:path*' &&
  (rule.has || []).some((condition) => condition.type === 'host' && condition.value === 'qulacrafts.com')
);
if (!hasCanonicalRedirect) failures.push('vercel.json: missing non-www to www canonical redirect');

// A replaced product image must update both its manifest fingerprint and the
// intrinsic dimensions in the PDP. This prevents stale layout metadata from
// silently shipping after gallery replacements.
const batchManifestPath = path.join(root, 'docs', 'product-batch-manifest-20260912.json');
const batchManifest = JSON.parse(fs.readFileSync(batchManifestPath, 'utf8'));
for (const product of batchManifest.products) {
  const htmlPath = path.join(root, product.slug);
  const html = fs.readFileSync(htmlPath, 'utf8');
  for (const image of product.imageOutputs) {
    const imagePath = path.join(root, image.path);
    if (!fs.existsSync(imagePath)) {
      failures.push(`${product.slug}: missing batch image ${image.path}`);
      continue;
    }
    const digest = crypto.createHash('sha256').update(fs.readFileSync(imagePath)).digest('hex');
    if (digest !== image.sha256) failures.push(`${image.path}: SHA-256 differs from batch manifest`);
    const escaped = image.path.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const tag = (html.match(new RegExp(`<img\\b[^>]*src=["']${escaped}["'][^>]*>`, 'i')) || [])[0] || '';
    if (!tag) failures.push(`${product.slug}: missing gallery image ${image.path}`);
    else if (!new RegExp(`\\bwidth=["']${image.width}["']`, 'i').test(tag) ||
             !new RegExp(`\\bheight=["']${image.height}["']`, 'i').test(tag)) {
      failures.push(`${product.slug}: stale dimensions for ${image.path}`);
    }
  }
}

if (failures.length) {
  console.error(`SEO checks failed (${failures.length}):`);
  for (const failure of failures.slice(0, 80)) console.error(`- ${failure}`);
  process.exit(1);
}

console.log(`SEO checks passed: ${indexable.length} indexable pages, unique metadata/canonicals, valid JSON-LD, complete image attributes, canonical host enforced.`);
