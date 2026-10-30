import test from 'node:test';
import assert from 'node:assert/strict';
import { canonicalLinks, sitemapPageUrls, validateSitemapUrls } from '../seo-url-guards.mjs';

const url = 'https://www.qulacrafts.com/p-example.html';
const expected = new Set([url]);

test('canonical supports attribute order, quotes, case and rel tokens', () => {
  assert.deepEqual(canonicalLinks(`<LINK href='${url}' data-rel='other' REL='alternate canonical'>`), [url]);
  assert.deepEqual(canonicalLinks(`<link rel=canonical href=${url}>`), [url]);
});

test('duplicate canonical tags remain visible, including identical duplicates', () => {
  assert.equal(canonicalLinks(`<link rel="canonical" href="${url}"><link href='${url}' rel='canonical'>`).length, 2);
});

test('missing href is counted as an invalid canonical, not silently dropped', () => {
  assert.deepEqual(canonicalLinks('<link rel="canonical">'), ['']);
  assert.deepEqual(canonicalLinks('<link data-rel="canonical" href="x">'), []);
});

test('commented and script-string canonical examples are not actual links', () => {
  assert.deepEqual(canonicalLinks(`<!-- <link rel="canonical" href="x"> --><script>const s='<link rel="canonical" href="x">';</script><link rel="canonical" href="${url}">`), [url]);
});

test('page locations exclude image locations, not unapproved page hosts', () => {
  const xml = `<urlset><url><loc>${url}</loc><image:image><image:loc>https://www.qulacrafts.com/assets/a.jpg</image:loc></image:image></url><url><loc>https://other.example/p.html</loc></url></urlset>`;
  assert.deepEqual(sitemapPageUrls(xml), [url, 'https://other.example/p.html']);
});

test('valid unique sitemap matches the indexable source set', () => {
  assert.deepEqual(validateSitemapUrls([url], expected), []);
});

test('duplicate locations fail even when set coverage is otherwise complete', () => {
  assert.match(validateSitemapUrls([url, url], expected).join('\n'), /duplicate page URL/);
});

for (const extra of [
  'https://other.example/p-example.html',
  'https://qulacrafts.com/p-example.html',
  'http://www.qulacrafts.com/p-example.html',
  `${url}?sort=price`, `${url}#variant`,
  'https://www.qulacrafts.com/thank-you.html',
  'https://www.qulacrafts.com/assets/a.jpg',
]) {
  test(`reject unapproved sitemap entry: ${extra}`, () => {
    assert.match(validateSitemapUrls([url, extra], expected).join('\n'), /non-indexable/);
  });
}

test('missing page location fails', () => {
  assert.match(validateSitemapUrls([], expected).join('\n'), /sitemap missing/);
});
