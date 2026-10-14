import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const slug = 'blog-custom-resin-polymer-clay-process.html';
const article = fs.readFileSync(path.join(root, slug), 'utf8');
const service = fs.readFileSync(path.join(root, 'customization.html'), 'utf8');
const resources = fs.readFileSync(path.join(root, 'resources.html'), 'utf8');
const sitemap = fs.readFileSync(path.join(root, 'sitemap.xml'), 'utf8');
const css = fs.readFileSync(path.join(root, 'assets/css/custom-design-process.css'), 'utf8');
const main = article.match(/<article class="custom-story">([\s\S]*?)<\/article>/)[1];
const schemas = [...article.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)].map(m => JSON.parse(m[1]));
const articleSchema = schemas.find(s => s['@type'] === 'BlogPosting');
assert.equal(articleSchema.mainEntityOfPage, 'https://www.qulacrafts.com/' + slug);
assert.equal(articleSchema.headline, main.match(/<h1>(.*?)<\/h1>/)[1]);
assert.equal(articleSchema.dateModified, '2026-10-14');
assert.equal((article.match(/<h1\b/g) || []).length, 1);
assert.equal((main.match(/class="custom-checkpoint"/g) || []).length, 8);
assert.equal((main.match(/class="custom-material-path/g) || []).length, 2);
assert(main.includes('AI-generated scenes'));
assert(main.includes('not a customer case study or factory photographs'));
assert(main.includes('Mold ownership, storage, reuse and exclusivity need a written agreement'));
assert(!/Emily|Carter|testimonial|guaranteed|\$\d|\b\d+[–-]\d+ (?:days|weeks)/i.test(main));
assert(css.includes('height:auto;object-fit:contain'));
for (const id of ['resin-customization', 'polymer-customization']) assert(service.includes('id="' + id + '"'));
for (const html of [service, resources]) assert(html.includes('href="' + slug + '"'));
assert(sitemap.includes('<loc>https://www.qulacrafts.com/' + slug + '</loc>'));
for (const filename of [slug, 'customization.html', 'resources.html']) {
  const html = fs.readFileSync(path.join(root, filename), 'utf8');
  for (const [, href] of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    if (/^(https?:|mailto:|tel:|data:)/.test(href)) continue;
    const [pathname, fragment] = href.split('?')[0].split('#');
    const target = path.join(root, pathname || filename);
    assert(fs.existsSync(target), `${filename}: missing ${href}`);
    if (fragment && target.endsWith('.html')) assert(fs.readFileSync(target, 'utf8').includes(`id="${fragment}"`), `${filename}: missing anchor ${href}`);
  }
}
const faq = schemas.find(s => s['@type'] === 'FAQPage').mainEntity;
const visibleFaq = [...main.matchAll(/<details><summary>(.*?)<\/summary><p>(.*?)<\/p><\/details>/g)];
assert.equal(faq.length, visibleFaq.length);
for (let i = 0; i < faq.length; i++) { assert.equal(faq[i].name, visibleFaq[i][1]); assert.equal(faq[i].acceptedAnswer.text, visibleFaq[i][2]); }
const png = fs.readFileSync(path.join(root, 'assets/images/custom-design-process/qula-custom-design-process.png'));
assert.equal(png.readUInt32BE(16), 1536);
assert.equal(png.readUInt32BE(20), 1024);
console.log(`Custom design guide passed: eight checkpoints, separate material paths, FAQ/schema parity, valid local links, uncropped 1536×1024 illustration (${crypto.createHash('sha256').update(png).digest('hex')}).`);
