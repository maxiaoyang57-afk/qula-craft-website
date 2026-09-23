import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const host = 'www.qulacrafts.com';
const base = `https://${host}/`;
const keyFile = '4e316ddf27bc705d6d3edbf5bcabf6e4.txt';
const keyPath = path.join(root, keyFile);
const key = fs.readFileSync(keyPath, 'utf8').trim();

const before = process.env.INDEXNOW_BEFORE || '';
const after = process.env.INDEXNOW_SHA || process.env.GITHUB_SHA || 'HEAD';

function git(args) {
  return execFileSync('git', args, { cwd: root, encoding: 'utf8' }).trim();
}

function changedFiles() {
  try {
    if (before && !/^0+$/.test(before)) {
      return git(['diff', '--name-only', before, after]).split(/\r?\n/).filter(Boolean);
    }
  } catch {}
  try {
    return git(['show', '--pretty=format:', '--name-only', after]).split(/\r?\n/).filter(Boolean);
  } catch {
    return [];
  }
}

const setupFiles = new Set([
  keyFile,
  '.github/workflows/indexnow.yml',
  'scripts/submit-indexnow.mjs',
  'scripts/check-indexnow.mjs',
]);

const initialPriorityPages = [
  'index.html',
  'products.html',
  'polymer-clay-sprinkles.html',
  'resin-charms.html',
  'acrylic-beads.html',
  'slime-charms.html',
  'glitter-sequins-fillers.html',
  'applications.html',
  'seasonal-collections.html',
  'guide-polymer-clay-sprinkles-bulk.html',
  'guide-clay-slices-vs-resin-charms-slime.html',
];

const files = changedFiles();
const candidates = new Set();

for (const file of files) {
  if (/^[^/]+\.html$/i.test(file)) candidates.add(file);
  const pdpImage = file.match(/^assets\/images\/pdp\/([^/]+)\//i);
  if (pdpImage) candidates.add(`p-${pdpImage[1].toLowerCase()}.html`);
}

if (files.some((file) => setupFiles.has(file))) {
  for (const page of initialPriorityPages) candidates.add(page);
}

const urls = [];
for (const file of candidates) {
  const full = path.join(root, file);
  if (!fs.existsSync(full)) continue;
  const html = fs.readFileSync(full, 'utf8');
  if (/<meta[^>]+name=["']robots["'][^>]+noindex/i.test(html)) continue;
  const canonical = (html.match(/<link\s+rel=["']canonical["']\s+href=["']([^"']+)["']/i) || [])[1];
  if (canonical && canonical.startsWith(base)) urls.push(canonical);
}

const uniqueUrls = [...new Set(urls)].slice(0, 10000);
if (!uniqueUrls.length) {
  console.log('IndexNow: no changed indexable URLs to submit.');
  process.exit(0);
}

const payload = {
  host,
  key,
  keyLocation: `${base}${keyFile}`,
  urlList: uniqueUrls,
};

const response = await fetch('https://api.indexnow.org/indexnow', {
  method: 'POST',
  headers: { 'content-type': 'application/json; charset=utf-8' },
  body: JSON.stringify(payload),
});

const responseText = await response.text();
if (![200, 202].includes(response.status)) {
  console.error(`IndexNow submission failed: HTTP ${response.status} ${responseText}`);
  process.exit(1);
}

console.log(`IndexNow accepted ${uniqueUrls.length} URL(s) with HTTP ${response.status}.`);
for (const url of uniqueUrls) console.log(`- ${url}`);
