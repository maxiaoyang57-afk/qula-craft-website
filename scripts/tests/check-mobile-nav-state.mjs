import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';

const root = new URL('../../', import.meta.url);
const mainJs = await readFile(new URL('assets/js/main.js', root), 'utf8');

assert.match(mainJs, /window\.addEventListener\('pageshow',closeNav\)/,
  'mobile navigation must reset when a page is restored from browser history');
assert.match(mainJs, /if\(e\.target\.closest&&e\.target\.closest\('a'\)\)closeNav\(\)/,
  'mobile navigation must close before following a menu link');
assert.match(mainJs, /aria-expanded/,
  'navigation toggle must expose its open state');

const version = '20260921-mobile-nav-back-state';
const files = (await readdir(root)).filter(name => name.endsWith('.html'));
let navPages = 0;

for (const file of files) {
  const html = await readFile(new URL(file, root), 'utf8');
  if (!html.includes('data-nav-toggle')) continue;
  navPages += 1;
  assert.match(html, /data-nav-toggle[^>]*|<button class="nav-toggle"[^>]*data-nav-toggle/,
    `${file}: missing navigation toggle`);
  assert.match(html, /aria-expanded="false"/,
    `${file}: navigation toggle must start closed`);
  assert.match(html, /id="site-navigation" data-nav-menu/,
    `${file}: navigation menu must have the shared accessible id`);
  assert.ok(html.includes(`assets/js/main.js?v=${version}`),
    `${file}: stale main.js cache version`);
}

assert.ok(navPages > 250, `expected site-wide coverage, found ${navPages} navigation pages`);
console.log(`Mobile navigation state checks passed for ${navPages} pages.`);
