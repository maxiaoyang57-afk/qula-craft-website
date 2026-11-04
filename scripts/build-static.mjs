import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { transform } from 'esbuild';
import { renderResinCardSpecs } from './resin-card-specs.mjs';
import { minify } from 'html-minifier-terser';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(root, 'dist');
await fs.rm(out, { recursive: true, force: true });
await fs.mkdir(out);
const entries = await fs.readdir(root, { withFileTypes: true });
const catalog = JSON.parse(await fs.readFile(path.join(root, 'assets/data/product-catalog.json'), 'utf8'));
const htmlEscape = value => String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
for (const entry of entries) {
  if (entry.isFile() && /\.(?:html|txt|xml|ico)$/.test(entry.name) ||
      entry.isDirectory() && ['assets', 'images', 'docs'].includes(entry.name)) {
    await fs.cp(path.join(root, entry.name), path.join(out, entry.name), { recursive: true });
  }
}

// Product selection is transient RFQ form state. Product/PDP URLs stay unchanged;
// previously shared query links continue to work in quote-v2.js.
const formStateLinks = text => text.replace(/quote\.html\?/g, 'quote.html#rfq:');
const fingerprints = new Map();
const savings = { js: { before: 0, after: 0, files: 0 }, css: { before: 0, after: 0, files: 0 }, html: { before: 0, after: 0, files: 0 } };
async function walk(dir) {
  const files = [];
  for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) files.push(...await walk(p));
    else files.push(p);
  }
  return files;
}
for (const file of await walk(path.join(out, 'assets'))) {
  const ext = path.extname(file);
  if (!['.js', '.css', '.json'].includes(ext)) continue;
  let code = await fs.readFile(file, 'utf8');
  const before = Buffer.byteLength(code);
  if (ext === '.json') {
    // Only inquiry URLs change; SKU identity, source facts and commercial values do not.
    code = formStateLinks(code);
    JSON.parse(code);
  } else {
    if (ext === '.js') code = formStateLinks(code);
    const result = await transform(code, { loader: ext.slice(1), minify: true, keepNames: true, legalComments: 'inline', charset: 'utf8' });
    if (result.warnings.length) throw new Error(`${path.relative(root, file)}: ${result.warnings.map(w => w.text).join('; ')}`);
    code = result.code;
    const stat = savings[ext.slice(1)];
    stat.before += before; stat.after += Buffer.byteLength(code); stat.files++;
    fingerprints.set(path.relative(out, file).split(path.sep).join('/'), crypto.createHash('sha256').update(code).digest('hex').slice(0, 12));
  }
  await fs.writeFile(file, code);
}

const analytics = await fs.readFile(path.join(root, 'assets/js/analytics.js'), 'utf8');
const panelContent = analytics.match(/panel\.innerHTML='([^']+)';/)?.[1];
if (!panelContent) throw new Error('Consent copy must come from the existing consent implementation');
const consent = '<section id="qula-analytics-consent" class="qc-consent" role="region" aria-labelledby="qc-consent-title" aria-describedby="qc-consent-description">' + panelContent + '</section>' +
  '<script>try{document.getElementById("qula-analytics-consent").hidden=!/^(www\\.)?qulacrafts\\.com$/i.test(location.hostname)||localStorage.getItem("qula_analytics_consent_v1")!==null}catch(e){}</script>';

function attr(tag, name) {
  return tag.match(new RegExp('\\b' + name + '=["\']([^"\']*)["\']', 'i'))?.[1];
}
function imagePreloads(html) {
  const hero = [...html.matchAll(/<img\b[^>]*>/gi)].map(m => m[0]).find(tag => attr(tag, 'fetchpriority') === 'high');
  if (!hero) return '';
  const picture = [...html.matchAll(/<picture\b[^>]*>([\s\S]*?)<\/picture>/gi)].find(m => m[1].includes(hero));
  const source = picture?.[1].match(/<source\b[^>]*>/i)?.[0];
  const link = (tag, media = '') => {
    const srcset = attr(tag, 'srcset');
    const href = attr(tag, 'src') || srcset?.split(',')[0].trim().split(/\s+/)[0];
    if (!href) return '';
    return '<link rel="preload" as="image" fetchpriority="high" href="' + href + '"' +
      (srcset ? ' imagesrcset="' + srcset + '" imagesizes="' + (attr(tag, 'sizes') || '100vw') + '"' : '') +
      (media ? ' media="' + media + '"' : '') + '>';
  };
  return source ? link(source, attr(source, 'media')) + link(hero, '(min-width: 721px)') : link(hero);
}

for (const entry of entries.filter(e => e.isFile() && e.name.endsWith('.html'))) {
  const file = path.join(out, entry.name);
  let html = await fs.readFile(file, 'utf8');
  const before = Buffer.byteLength(html);
  if (entry.name === 'resin-charms.html') html = await renderResinCardSpecs(root, html);
  html = html.replace(/\bhref=(["'])([^"']+)\1/gi, (all, quote, url) => {
    if (/^\/?index\.html(?:#.*)?$/.test(url)) return 'href=' + quote + url.replace(/^\/?index\.html/, '/') + quote;
    if (!/^(?:https:\/\/www\.qulacrafts\.com\/)?\/?quote\.html\?/.test(url)) return all;
    return 'href=' + quote + formStateLinks(url) + quote;
  });
  if (['seasonal-collections.html', 'guide-polymer-clay-sprinkles-bulk.html'].includes(entry.name)) {
    // These above-the-fold images were lazy-loaded in the Lighthouse sample.
    html = html.replace(/(<main\b[\s\S]*?<img\b)([^>]*>)/i, (all, prefix, attrs) => {
      attrs = attrs.replace(/\sloading=["']lazy["']/i, ' loading="eager"');
      if (!/\bfetchpriority=/.test(attrs)) attrs = ' fetchpriority="high"' + attrs;
      if (entry.name.startsWith('guide-') && !/\bsrcset=/.test(attrs)) {
        attrs = ' srcset="assets/images/responsive-20261029/polymer-clay-slices-cover-v2-680f8f51-360w.webp 360w, assets/images/responsive-20261029/polymer-clay-slices-cover-v2-680f8f51-640w.webp 640w, assets/images/responsive-20261029/polymer-clay-slices-cover-v2-680f8f51-960w.webp 960w" sizes="(max-width: 900px) calc(100vw - 48px), 860px"' + attrs;
      }
      return prefix + attrs;
    });
  }
  if (entry.name === 'guide-seasonal-craft-calendar.html') {
    // The complete repository graph confirmed this SKU really had only one
    // incoming page; most other sampled warnings were a 100-page crawl artifact.
    const products = ['p-yx4102.html', 'p-yx163.html', 'p-yx4057.html', 'p-yx421.html'].map(pdp => {
      const product = catalog.categories.flatMap(c => c.products).find(p => p.pdp === pdp);
      if (!product) throw new Error('Missing published seasonal comparison product: ' + pdp);
      return '<a href="' + product.pdp + '">' + htmlEscape(product.titleFull || product.title) + '</a>';
    });
    html = html.replace('</main>', '<aside class="container guide-note">Compare current seasonal products: ' + products.join(' · ') + '.</aside></main>');
  }
  if (html.includes('assets/js/analytics.js')) {
    // Parse-time markup and its CSS reserve space before the first paint. The
    // existing consent code still owns all choices, cookies and tracking gates.
    html = html.replace('</head>', '<link rel="stylesheet" href="assets/css/analytics-consent.css" data-consent-style></head>');
    html = html.replace(/<main\b/, consent + '<main');
  }
  const preloads = imagePreloads(html);
  if (preloads) {
    html = html.replace(/<link\b(?=[^>]*\brel=["']preload["'])(?=[^>]*\bas=["']image["'])[^>]*>/gi, '');
    // Discover hero images before the inlined CSS, while keeping charset first.
    const marker = html.match(/<meta\b(?=[^>]*\bname=["']viewport["'])[^>]*>/i)?.[0] || '<head>';
    html = html.replace(marker, marker + preloads);
  }
  html = html.replace(/\b(href|src)=(["'])(\/?assets\/[^"'?#]+)(?:\?[^"']*)?\2/g, (all, key, quote, asset) => {
    const version = fingerprints.get(asset.replace(/^\//, ''));
    return version ? `${key}=${quote}${asset}?v=${version}${quote}` : all;
  });
  html = await minify(html, { collapseWhitespace: true, conservativeCollapse: true, removeComments: true, minifyCSS: true, minifyJS: false });
  await fs.writeFile(file, html);
  savings.html.before += before; savings.html.after += Buffer.byteLength(html); savings.html.files++;
}
console.log(JSON.stringify({ output: 'dist', savings }, null, 2));
