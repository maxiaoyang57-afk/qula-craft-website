// Small validators for this site's generated HTML and sitemap format.
// They validate source output, not Google's selected canonical or live indexing.
function attribute(tag, name) {
  const match = tag.match(new RegExp(`\\s${name}\\s*=\\s*(?:"([^"]*)"|'([^']*)'|([^\\s>]+))`, 'i'));
  return match ? (match[1] ?? match[2] ?? match[3]) : '';
}

export function canonicalLinks(html) {
  const markup = html.replace(/<!--[\s\S]*?-->/g, '').replace(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi, '');
  return [...markup.matchAll(/<link\b[^>]*>/gi)]
    .map(([tag]) => ({ rel: attribute(tag, 'rel'), href: attribute(tag, 'href') }))
    .filter(({ rel }) => rel.toLowerCase().split(/\s+/).includes('canonical'))
    .map(({ href }) => href);
}

export function sitemapPageUrls(xml) {
  // Deliberately exclude image:loc while retaining ALL plain page loc elements.
  // General XML well-formedness is covered by gates_full.py.
  return [...xml.replace(/<!--[\s\S]*?-->/g, '').matchAll(/<loc\s*>([\s\S]*?)<\/loc\s*>/g)]
    .map((match) => match[1].trim());
}

export function validateSitemapUrls(urls, expectedUrls) {
  const failures = [];
  const seen = new Set();
  for (const url of urls) {
    if (seen.has(url)) failures.push(`sitemap duplicate page URL ${url}`);
    seen.add(url);
    // Exact membership also rejects foreign/apex hosts, HTTP, query strings,
    // fragments, assets and noindex pages without silently normalizing them.
    if (!expectedUrls.has(url)) failures.push(`sitemap includes non-indexable ${url}`);
  }
  for (const url of expectedUrls) if (!seen.has(url)) failures.push(`sitemap missing ${url}`);
  return failures;
}
