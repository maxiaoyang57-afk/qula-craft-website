import { readdirSync, readFileSync } from 'node:fs';

const pages = readdirSync('dist').filter(name => /^resin-charms(?:-page-\d+)?\.html$/.test(name));
const pagesBySku = new Map(pages.flatMap(name =>
  [...readFileSync('dist/' + name, 'utf8').matchAll(/\bdata-sku="([^"]+)"/g)]
    .map(([, sku]) => [sku, '/' + name])));

export function resinPageForSku(sku) {
  const page = pagesBySku.get(sku);
  if (!page) throw new Error('No published resin catalog card for ' + sku);
  return page;
}
