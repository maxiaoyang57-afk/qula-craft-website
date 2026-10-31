"""Apply the owner's fixed nine-category scope while preserving old SKU pages."""
import html
import json
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / 'scripts/data/catalog-scope-20261031.json').read_text())
ARCHIVED_SKUS = {p['sku'] for p in POLICY['products']}


def apply_scope():
    cp = ROOT / 'assets/data/product-catalog.json'
    cat = json.loads(cp.read_text())
    prior = [p for c in cat['categories'] for p in c['products']] + cat.get('archivedProducts', [])
    by_pdp = {p['pdp']: p for p in prior}
    archived = []
    for source in POLICY['products']:
        row = by_pdp[source['pdp']]
        if row['sku'] != source['sku'] or row['image'] != source['image']:
            raise ValueError('Archived identity mismatch: ' + source['sku'])
        archived.append(row)
    cat['categories'] = [c for c in cat['categories'] if c['slug'] not in POLICY['archivedCategories']]
    if [c['slug'] for c in cat['categories']] != POLICY['activeCategories']:
        raise ValueError('Unapproved public category')
    active = [p for c in cat['categories'] for p in c['products']]
    if any(p['sku'] in ARCHIVED_SKUS for p in active):
        raise ValueError('Archived SKU remains in public catalog')
    cat['archivedProducts'] = archived
    cat.update(totalProducts=len(active), totalImages=len(active))
    cp.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding='utf-8')
    archived_files = {p['pdp'] for p in archived}
    old_category = 'decorative-craft-accessories.html'
    notice = '<section class="section" data-catalog-archive><div class="container"><p><strong>Previous catalog reference.</strong> This item is outside our current catalog. Original product information is retained for reference; contact us with the SKU to review your request.</p><a class="btn btn-light" href="products.html">Browse the current catalog</a></div></section>'
    for path in ROOT.glob('*.html'):
        text = path.read_text(encoding='utf-8')
        if path.name == old_category:
            text = re.sub(r'<main\b[^>]*>.*?</main>', '<main id="main"><section class="section"><div class="container"><h1>Previous decorative selection</h1><p>This selection is no longer part of the current catalog. For a previous product reference, contact us with its SKU.</p><a class="btn btn-primary" href="products.html">Browse the current catalog</a></div></section></main>', text, flags=re.S)
            text = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '' if json.loads(m[0].split('>',1)[1].rsplit('</script>',1)[0]).get('@type') in ['ItemList','CollectionPage','FAQPage'] else m[0], text, flags=re.S)
        if path.name in archived_files:
            text = re.sub(r'<section class="section" data-catalog-archive>.*?</section>', '', text, flags=re.S)
            text = re.sub(r'(<main\b[^>]*>)', lambda m: m[1] + notice, text, count=1)
            text = re.sub(r'<a([^>]*?)href="decorative-craft-accessories.html"([^>]*)>[^<]*</a>', r'<a\1href="products.html"\2>Current catalog</a>', text)
            def quote_link(m):
                url = html.unescape(m[1])
                if not url.startswith('quote.html?'):
                    return m[0]
                parts = urlsplit(url)
                params = dict(parse_qsl(parts.query))
                params['category'] = 'Other'
                return 'href="' + html.escape('quote.html?' + urlencode(params), quote=True) + '"'
            text = re.sub(r'href="([^"]+)"', quote_link, text)
            # Related cards would otherwise expose another archived item.
            text = re.sub(r'<section class="section section-soft">.*?</section>', '', text, flags=re.S)
        # Remove category entry cards from home/directory and the obsolete RFQ choice.
        text = re.sub(r'<section\b[^>]*>.*?</section>', lambda m: '' if '<h2><a href="' + old_category + '"' in m[0] else m[0], text, flags=re.S)
        text = re.sub(r'<article class="(?:category-card|image-card)[^"]*"[^>]*>.*?</article>', lambda m: '' if 'href="' + old_category + '"' in m[0] else m[0], text, flags=re.S)
        text = re.sub(r'<a class="[^"]*category[^"]*"[^>]*href="decorative-craft-accessories.html"[^>]*>.*?</a>', '', text, flags=re.S)
        text = re.sub(r'<option(?: value="Decorative Craft Accessories")?>Decorative Craft Accessories</option>', '', text)
        if path.name in archived_files or path.name == old_category:
            text = re.sub(r'(<meta\s+name="robots"\s+content=")[^"]*(")', r'\g<1>noindex,follow\2', text)
            def breadcrumb(m):
                data = json.loads(m[2])
                if data.get('@type') != 'BreadcrumbList':
                    return m[0]
                data['itemListElement'] = [i for i in data['itemListElement'] if not str(i.get('item', '')).endswith('/' + old_category)]
                for n, item in enumerate(data['itemListElement'], 1): item['position'] = n
                return m[1] + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + m[3]
            text = re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)', breadcrumb, text, flags=re.S)
        path.write_text(text, encoding='utf-8')
    # Remove only the unlisted pages; retain existing images and original product data.
    sp = ROOT / 'sitemap.xml'
    xml = sp.read_text()
    excluded = archived_files | {old_category}
    xml = re.sub(r'<url>.*?</url>', lambda m: '' if any('<loc>https://www.qulacrafts.com/' + f + '</loc>' in m[0] for f in excluded) else m[0], xml, flags=re.S)
    sp.write_text('\n'.join(line.rstrip() for line in xml.splitlines()).rstrip() + '\n')
    full = ROOT / 'llms-full.txt'
    value = full.read_text()
    value = re.sub(r'## Decorative Craft Accessories\n.*?(?=\n## |\Z)', '', value, flags=re.S)
    full.write_text(value.rstrip() + '\n')
    print(f'Public scope: {len(cat["categories"])} categories, {len(active)} products; {len(archived)} old SKU pages retained.')


if __name__ == '__main__':
    apply_scope()
