import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const read = name => fs.readFileSync(path.resolve(name), 'utf8');
const pages = fs.readdirSync('.').filter(name => name.endsWith('.html'));
const metadata = html => [...html.matchAll(/<script\b[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)].map(m => JSON.parse(m[1]));

test('build preserves every public and archived page, canonical and structured data', () => {
  assert.equal(fs.readdirSync('dist').filter(name => name.endsWith('.html')).length, pages.length);
  for (const page of pages) {
    const before = read(page), after = read('dist/' + page);
    assert.deepEqual(metadata(after), metadata(before), page + ' JSON-LD');
    for (const pattern of [/<link rel="canonical" href="([^"]+)"/, /<meta name="robots" content="([^"]+)"/, /<h1\b[^>]*>([\s\S]*?)<\/h1>/]) {
      const normalize = value => value?.replace(/\s+/g, ' ').trim();
      assert.equal(normalize(after.match(pattern)?.[1]), normalize(before.match(pattern)?.[1]), page + ' protected metadata');
    }
    assert(!/href=["'](?:https:\/\/www\.qulacrafts\.com\/)?\/?quote\.html\?/.test(after), page + ' duplicate inquiry queries');
  }
});

test('all catalog facts and all inquiry parameter values survive the build', () => {
  for (const name of ['product-catalog.json', 'pdp-data.json', 'pdp-copy.json']) {
    const before = JSON.parse(read('assets/data/' + name).replace(/quote\.html\?/g, 'quote.html#rfq:'));
    assert.deepEqual(JSON.parse(read('dist/assets/data/' + name)), before, name);
  }
  for (const page of pages) {
    const before = read(page);
    for (const [, quote, query] of before.matchAll(/href=(["'])(?:https:\/\/www\.qulacrafts\.com\/)?\/?quote\.html\?([^"']+)\1/g)) {
      const decode = value => value.replace(/&amp;/g, '&').replace(/&#39;/g, "'").replace(/&quot;/g, '"');
      const expected = [...new URLSearchParams(decode(query))];
      const after = read('dist/' + page);
      const matches = [...after.matchAll(/href=(["'])(?:https:\/\/www\.qulacrafts\.com\/)?\/?quote\.html#rfq:([^"']+)\1/g)];
      assert(matches.some(m => JSON.stringify([...new URLSearchParams(decode(m[2]))]) === JSON.stringify(expected)), page + ' RFQ context');
    }
  }
});

test('consent is present at parse time and all local scripts and styles use built fingerprints', () => {
  for (const page of pages) {
    const html = read('dist/' + page);
    assert.equal((html.match(/id="qula-analytics-consent"/g) || []).length, 1, page);
    assert(html.indexOf('id="qula-analytics-consent"') < html.indexOf('<main'), page);
    for (const [, url] of html.matchAll(/(?:src|href)="(\/?assets\/[^"?#]+\.(?:js|css)\?v=[^"]+)"/g)) {
      assert(/\?v=[a-f0-9]{12}$/.test(url), page + ' ' + url);
      assert(fs.existsSync('dist/' + url.replace(/^\//, '').split('?')[0]), url);
    }
  }
  assert(!read('dist/quote.html').includes('hreflang='));
});
