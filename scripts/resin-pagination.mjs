const category = 'resin-charms.html';
const pageSize = 48;
const cardPattern = /<article\b[^>]*class="product-card"[^>]*>[\s\S]*?<\/article>/g;
const schemaPattern = /(<script type="application\/ld\+json">)([\s\S]*?)(<\/script>)/g;

function pageName(number) {
  return number === 1 ? category : `resin-charms-page-${number}.html`;
}

function pagination(number, count) {
  if (count === 1) return '';
  const link = (page, label, attributes = '') =>
    `<a class="btn btn-sm btn-light" href="${pageName(page)}"${attributes}>${label}</a>`;
  return `<nav class="hero-actions" aria-label="Resin catalog pages">
    ${number > 1 ? link(number - 1, 'Previous', ' rel="prev"') : ''}
    ${Array.from({ length: count }, (_, index) => {
      const page = index + 1;
      return page === number
        ? `<span class="pill soft" aria-current="page">${page}</span>`
        : link(page, page, ` aria-label="Page ${page}"`);
    }).join('')}
    ${number < count ? link(number + 1, 'Next', ' rel="next"') : ''}
  </nav>`;
}

export function buildResinPages(html) {
  const originalCards = [...html.matchAll(cardPattern)];
  const grid = html.match(/<div class="product-grid compact"[^>]*data-mobile-browse[^>]*>/);
  const first = originalCards[0];
  const last = originalCards.at(-1);
  const end = last?.index + last?.[0].length;
  if (!grid || !first || grid.index + grid[0].length > first.index ||
      html.slice(grid.index + grid[0].length, end).replace(cardPattern, '').trim() ||
      !html.slice(end).startsWith('</div>')) {
    throw new Error('Resin catalog cards must form one contiguous product grid');
  }
  const schema = [...html.matchAll(schemaPattern)].map(([, , text]) => JSON.parse(text));
  const list = schema.find(node => node['@type'] === 'ItemList');
  const collection = schema.find(node => node['@type'] === 'CollectionPage');
  if (!collection || list?.itemListElement?.length !== originalCards.length) {
    throw new Error('Resin catalog structured data must cover every product card');
  }
  const products = originalCards.map(([markup], index) => {
    const url = markup.match(/<h3>\s*<a\b[^>]*href="([^"]+)"/)?.[1];
    if (!url || new URL(url, collection.url).href !== list.itemListElement[index].url) {
      throw new Error(`Resin card and its structured data differ at item ${index + 1}`);
    }
    return markup;
  });
  const count = Math.ceil(products.length / pageSize);
  const main = html.match(/<main id="main">[\s\S]*?<\/main>/)?.[0];
  if (!main) throw new Error('Missing resin catalog main content');
  const pages = new Map();

  for (let number = 1; number <= count; number++) {
    const filename = pageName(number);
    const url = new URL(filename, collection.url).href;
    const start = (number - 1) * pageSize;
    const endIndex = Math.min(start + pageSize, products.length);
    const listing = `<p>Showing ${start + 1}–${endIndex} of ${products.length} resin charms. <a href="products.html">Search by SKU or keyword</a></p>
      ${grid[0]}${products.slice(start, endIndex).join('\n')}</div>
      ${pagination(number, count)}`;
    const title = `Bulk Resin Charms &amp; Flatback Cabochons – Page ${number} | Qula Craft`;
    const description = `Browse resin charms ${start + 1}–${endIndex} in the Qula Craft wholesale catalog. Compare designs, dimensions and packing by SKU.`;
    let page = number === 1
      ? html.slice(0, grid.index) + listing + html.slice(end + '</div>'.length)
      : html.replace(main, () => `<main id="main"><section class="section section-soft" id="resin-catalog"><div class="container">
          <nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="products.html">Products</a> / <a href="${category}">Resin Charms</a> / <span>Page ${number}</span></nav>
          <h1>Bulk Resin Charms &amp; Flatback Cabochons – Page ${number}</h1>${listing}</div></section></main>`)
        .replace(/<title>[^<]*<\/title>/, () => `<title>${title}</title>`)
        .replace(/(<meta (?:name="description"|property="og:description") content=")[^"]+/, `$1${description}`)
        .replace(/(<meta property="og:title" content=")[^"]+/, `$1${title}`)
        .replace(/(<(?:link rel="(?:canonical|alternate)"[^>]*?href|meta property="og:url" content)=")https:\/\/www\.qulacrafts\.com\/resin-charms\.html/g, `$1${url}`);

    page = page.replace(schemaPattern, (match, open, body, close) => {
      const node = JSON.parse(body);
      if (node['@type'] === 'ItemList') {
        node.itemListElement = list.itemListElement.slice(start, endIndex)
          .map((item, index) => ({ ...item, position: index + 1 }));
        node.numberOfItems = node.itemListElement.length;
      } else if (number === 1) return match;
      else if (node['@type'] === 'FAQPage') return '';
      else if (node['@type'] === 'CollectionPage') {
        node.name = `Bulk Resin Charms & Flatback Cabochons – Page ${number}`;
        node.description = description;
        node.url = url;
      } else if (node['@type'] === 'BreadcrumbList') {
        node.itemListElement.push({ '@type': 'ListItem', position: node.itemListElement.length + 1, name: `Page ${number}`, item: url });
      } else return match;
      return open + JSON.stringify(node) + close;
    });
    pages.set(filename, page);
  }
  return pages;
}
