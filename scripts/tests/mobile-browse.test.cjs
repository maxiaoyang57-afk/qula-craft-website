const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.resolve(__dirname, '../../assets/js/mobile-browse.js'), 'utf8');

// Execute the production initializer. This small DOM fixture checks card
// preservation and user actions without launching a browser or sending requests.
function fixture({ count = 30, mobile = true, hash = '' } = {}) {
  let document;
  const scrolls = [], listeners = {}, observers = [];
  class Node {
    constructor(tag = 'div') {
      this.tagName = tag.toUpperCase(); this.children = []; this.dataset = {};
      this.attrs = new Map(); this.style = {}; this.hidden = false;
      this.events = {}; this.id = ''; this.className = ''; this.textContent = '';
    }
    appendChild(node) { this.children.push(node); node.parentElement = this; return node; }
    append(...nodes) { nodes.forEach(node => this.appendChild(node)); }
    after(node) { this.afterNode = node; }
    setAttribute(name, value) { this.attrs.set(name, value); }
    removeAttribute(name) { this.attrs.delete(name); }
    hasAttribute(name) { return this.attrs.has(name); }
    contains(node) { return this === node || this.children.some(child => child.contains(node)); }
    querySelector() { return this.children.find(child => child.tagName === 'A') || null; }
    addEventListener(name, fn) { this.events[name] = fn; }
    focus() { document.activeElement = this; }
    scrollIntoView(options) { scrolls.push({ node: this, options }); }
  }
  const grid = new Node();
  grid.dataset = { mobileInitial: '12', mobileStep: '12', mobileLabel: 'products' };
  for (let i = 0; i < count; i++) {
    const card = new Node('article'); card.id = 'card-' + i;
    const link = new Node('a'); link.href = 'p-sku-' + i + '.html';
    card.appendChild(link); grid.appendChild(card);
  }
  function find(root, id) {
    if (root.id === id) return root;
    for (const child of root.children) { const found = find(child, id); if (found) return found; }
    return null;
  }
  document = {
    activeElement: new Node('body'),
    querySelectorAll: selector => { assert.equal(selector, '[data-mobile-browse]'); return [grid]; },
    getElementById: id => find(grid, id) || (grid.afterNode && find(grid.afterNode, id)),
    createElement: tag => new Node(tag),
  };
  const media = { matches: mobile, addEventListener: (name, fn) => { assert.equal(name, 'change'); media.change = fn; } };
  const window = {
    location: { hash }, matchMedia: () => media,
    addEventListener: (name, fn) => { listeners[name] = fn; },
  };
  class MutationObserver {
    constructor(fn) { this.notify = fn; observers.push(this); }
    observe() {}
  }
  vm.runInNewContext(source, { document, window, MutationObserver, queueMicrotask, requestAnimationFrame: fn => fn() });
  const controls = grid.afterNode;
  const actions = controls.children[1].children;
  return {
    grid, document, controls, scrolls, window,
    more: actions[0], all: actions[1], fewer: actions[2],
    visible: () => grid.children.filter(card => !card.hidden && card.style.display !== 'none' && !card.hasAttribute('data-mobile-browse-hidden')),
    resize(value) { media.matches = value; media.change(); },
    event(name) { listeners[name](); },
    filter(indices) {
      grid.children.forEach((card, index) => { card.style.display = indices.includes(index) ? '' : 'none'; });
      observers[0].notify([{ type: 'attributes', target: grid.children[0], attributeName: 'style' }]);
    },
    inserted() { observers[0].notify([{ type: 'childList', target: grid }]); },
  };
}

test('phone paging keeps every original card/link and focuses the newly revealed range', () => {
  const f = fixture();
  const original = [...f.grid.children];
  assert.equal(f.visible().length, 12);
  assert.equal(f.controls.children[0].textContent, 'Showing 12 of 30 products');
  assert.equal(f.controls.attrs.get('aria-label'), 'Browse products');
  assert.equal(f.more.attrs.get('aria-label'), 'Show 12 more products');
  assert.equal(f.all.textContent, 'Show all 30 products');
  f.more.events.click();
  assert.equal(f.visible().length, 24);
  assert.equal(f.document.activeElement, original[12].children[0]);
  assert.equal(f.scrolls.at(-1).node, original[12]);
  f.all.events.click();
  assert.equal(f.visible().length, 30);
  assert.equal(f.document.activeElement, original[24].children[0]);
  assert.equal(f.more.hidden, true);
  assert.deepEqual(f.grid.children, original);
  assert.deepEqual(f.grid.children.map(card => card.children[0].href), original.map(card => card.children[0].href));
});

test('filters consider later cards and reset pagination without overriding filter visibility', async () => {
  const f = fixture();
  f.filter([26, 28, 29]);
  await new Promise(setImmediate);
  assert.deepEqual(f.visible().map(card => card.id), ['card-26', 'card-28', 'card-29']);
  assert.equal(f.controls.children[0].textContent, 'Showing 3 of 3 products');
  f.filter([]);
  await new Promise(setImmediate);
  assert.equal(f.visible().length, 0);
  f.filter(Array.from({ length: 30 }, (_, i) => i));
  await new Promise(setImmediate);
  assert.equal(f.visible().length, 12);
  assert.equal(f.grid.children.length, 30);
});

test('desktop, resize and printing expose all cards; returning to phone restores paging', () => {
  const f = fixture({ mobile: false });
  assert.equal(f.visible().length, 30);
  assert.equal(f.controls.hidden, true);
  f.resize(true);
  assert.equal(f.visible().length, 12);
  f.event('beforeprint');
  assert.equal(f.visible().length, 30);
  assert.equal(f.controls.hidden, true);
  f.event('afterprint');
  assert.equal(f.visible().length, 12);
  f.resize(false);
  assert.equal(f.visible().length, 30);
});

test('initial fragments and later hash navigation reveal the requested hidden card', () => {
  const f = fixture({ hash: '#card-25' });
  assert.equal(f.visible().length, 30);
  assert.equal(f.scrolls.at(-1).node.id, 'card-25');
  const second = fixture();
  second.window.location.hash = '#card-29';
  second.event('hashchange');
  assert.equal(second.visible().length, 30);
  assert.equal(second.scrolls.at(-1).node.id, 'card-29');
  assert.equal(second.fewer.hidden, true, 'Do not offer a collapse that would hide the current fragment');
  second.window.location.hash = '#%broken';
  assert.doesNotThrow(() => second.event('hashchange'));
  const middle = fixture({ hash: '#card-13' });
  assert.equal(middle.visible().length, 24);
  middle.all.events.click();
  middle.fewer.events.click();
  assert.equal(middle.visible().length, 24, 'Collapse can shorten the list while keeping the fragment reachable');
  assert.equal(middle.fewer.hidden, true);
});

test('collapse restores the short view with a visible control holding keyboard focus', () => {
  const f = fixture();
  f.all.events.click();
  f.fewer.events.click();
  assert.equal(f.visible().length, 12);
  assert.equal(f.document.activeElement, f.more);
  assert.equal(f.more.hidden, false);
  assert.equal(f.fewer.hidden, true);
  assert.equal(f.scrolls.at(-1).node, f.grid);
});

test('newly inserted cards remain in the count and can be revealed without replacing existing cards', async () => {
  const f = fixture();
  const Node = f.grid.children[0].constructor;
  const card = new Node('article'); card.id = 'added-card';
  const link = new Node('a'); link.href = 'p-new-original.html';
  card.appendChild(link); f.grid.appendChild(card); f.inserted();
  await new Promise(setImmediate);
  assert.equal(f.all.textContent, 'Show all 31 products');
  f.all.events.click();
  assert.equal(f.visible().length, 31);
  assert.equal(f.grid.children.at(-1), card);
  assert.equal(link.href, 'p-new-original.html');
});

test('resizing cannot hide the product link that currently holds keyboard focus', () => {
  const f = fixture({ mobile: false });
  f.grid.children[29].children[0].focus();
  f.resize(true);
  assert.equal(f.visible().length, 30);
  assert.equal(f.document.activeElement, f.grid.children[29].children[0]);
});

test('source HTML is not pre-hidden and print rules cannot leave paged cards missing', () => {
  const root = path.resolve(__dirname, '../..');
  const home = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
  const category = fs.readFileSync(path.join(root, 'resin-charms.html'), 'utf8');
  assert.doesNotMatch(home + category, /data-mobile-browse-hidden/);
  assert.match(home, /data-mobile-initial="4"[^>]*data-mobile-label="product categories"/);
  assert.match(category, /data-mobile-initial="12"/);
  const css = fs.readFileSync(path.join(root, 'assets/css/mobile-browse.css'), 'utf8');
  assert.match(css, /@media screen and \(max-width:720px\)/);
  assert.match(css, /@media print[\s\S]*\[data-mobile-browse\]>\*\{display:block!important/);
});
