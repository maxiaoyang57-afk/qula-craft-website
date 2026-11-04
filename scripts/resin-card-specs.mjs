import fs from 'node:fs/promises';
import path from 'node:path';

const escapeText = text => text.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');

function cardSize(specs) {
  const value = [specs.Size, specs.Dimensions, specs['Reference size'], specs['Size reference']]
    .find(text => typeof text === 'string' && /\d\s*(?:mm|cm)\b/i.test(text));
  // Keep approximation, ranges and design-specific qualifications from the source.
  return value?.replace(/(?<=\d)\s*[x×]\s*(?=\d)/gi, ' × ')
    .replace(/(approximately|approx\.)(?=\d)/gi, '$1 ')
    .replace(/(\d)(mm|cm)\b/gi, '$1 $2').trim() || '';
}

function cardPack(specs) {
  const value = [specs['Source packing'], specs['Standard pack'], specs['Pack reference'], specs.Packaging]
    .find(text => typeof text === 'string' && /\d+\s*(?:pcs?|pieces?|sets?)\s*(?:\/|per\s+)\s*(?:bag|sleeve|batch|set)\b/i.test(text));
  if (!value) return '';
  return value.replace(/; custom packing by inquiry$/i, '')
    .replace(/\s*\(live official product attribute,[^)]*\)$/i, '')
    .replace(/(\d+)\s*(pcs?|pieces?|sets?)\s*(?:\/|per\s+)\s*(bag|sleeve|batch|set)\b/gi,
      (_, count, unit, container) => count + ' ' + (/^set/i.test(unit) ? unit.toLowerCase() : Number(count) === 1 ? 'pc' : 'pcs') + '/' + container.toLowerCase());
}

export async function renderResinCardSpecs(root, html) {
  const readData = async name => JSON.parse(await fs.readFile(path.join(root, 'assets/data', name), 'utf8'));
  const [products, verified] = await Promise.all([readData('pdp-data.json'), readData('verified-product-specs.json')]);
  const byPage = new Map(products.filter(p => p.categorySlug === 'resin-charms')
    .map(p => ['p-' + p.assetKey + '.html', p]));
  return html.replace(/<article\b[^>]*class="product-card"[^>]*>[\s\S]*?<\/article>/g, card => {
    const heading = card.match(/<h3>\s*<a\b[^>]*href="([^"]+)"[^>]*>[\s\S]*?<\/a>\s*<\/h3>/);
    const product = byPage.get(heading?.[1]);
    if (!product) throw new Error('Missing resin card specification source: ' + heading?.[1]);
    const specs = { ...product.specs, ...verified[product.sku] };
    const label = [cardSize(specs), cardPack(specs)].filter(Boolean).join(' · ');
    const line = label ? '<small class="card-specs">' + escapeText(label) + '</small>' : '';
    return card.replace(/<small class="card-specs">[^<]*<\/small>/g, '')
      .replace(heading[0], () => heading[0] + line);
  });
}
