"""Build a buyer-facing photo-to-components guide from existing catalog facts."""
import html
import json
import re
from pathlib import Path
from urllib.parse import urlencode
from PIL import Image
from gen_guides import build

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'guide-find-craft-supplies-from-photo.html'
BASE = 'https://www.qulacrafts.com/'
PRODUCTS = {p['assetKey']: p for p in json.loads((ROOT/'assets/data/pdp-data.json').read_text())}
SELECTION = [
 ('rw26801', 'Little fried eggs for a phone case', 'Miniature fried-egg resin decorations', 'Check the back, height and adhesive on the actual case. These no-hole pieces are not ready-to-hang charms.'),
 ('yx693', 'Tiny pink strawberries for slime', 'Pink strawberry polymer clay slices', 'Check thickness and performance in your own formula. The nail tip shown in the source photograph is a styling prop.'),
 ('yx329', 'Small light green leaves', 'Green leaf polymer clay slices', 'Compare the leaf shape and listed size with your layout; there is no confirmed included hanging fitting.'),
 ('ya425', 'Pastel heart beads for a bag charm', 'Heart acrylic beads', 'Compare the listed hole with your cord, rod or connector. A pen in the photograph does not establish fit.'),
 ('cdk070', 'Colorful rings for keychains', 'Colorful metal split key rings', 'Hardware only. Check ring thickness, opening and the connection to every other component.'),
]

def esc(s): return html.escape(str(s), quote=True)

def inquiry(key=None):
    data={'source':'photo-sourcing-guide','entry_page':'/'+SLUG,'entry_title':'Find Craft Supplies from a Photo','application':'Reference-photo sourcing: identify the pictured components, compare existing options and confirm size, attachment, quantity and packing.'}
    if key:
        p=PRODUCTS[key]
        data.update(product=p['titleFull'],sku=p['sku'],image=p['imagesLocal'][0],category={'Keychain':'Keychains','Polymer Clay Slices':'Polymer Clay Sprinkles','Plastic/Acrylic Beads':'Acrylic Beads','Plastic Beads':'Acrylic Beads'}.get(p['category'],p['category']))
    return 'quote.html?'+urlencode(data)

def cards():
    out=[]
    for key,question,label,note in SELECTION:
        p=PRODUCTS[key]; specs=p['specs']; src=p['imagesLocal'][0]
        w,h=Image.open(ROOT/src).size
        assert specs.get('Material') and specs.get('Size'), key
        pack=specs.get('Standard pack') or specs.get('Pack reference')
        facts=[('Listed material',specs['Material']),('Listed size',specs['Size'])]
        if specs.get('Hole diameter'): facts.append(('Listed hole',specs['Hole diameter']))
        if specs.get('Hole'): facts.append(('Hole',specs['Hole']))
        if pack: facts.append(('Reference pack',pack))
        out.append(f'<article style="min-width:0;border:1px solid #eadde3;border-radius:16px;padding:18px"><p class="small-note">Looking for “{esc(question)}”?</p><a href="p-{key}.html"><img src="{esc(src)}" alt="{esc(p["sku"]+": "+label)}" width="{w}" height="{h}" loading="lazy" style="display:block;width:100%;height:220px;object-fit:contain"></a><h3><a href="p-{key}.html">{esc(p["sku"])} · {esc(label)}</a></h3><dl>'+''.join(f'<dt><b>{esc(k)}</b></dt><dd style="margin:0 0 8px">{esc(v)}</dd>' for k,v in facts)+f'</dl><p>{esc(note)}</p><p><a href="p-{key}.html">Product details →</a></p><a class="btn btn-card" data-photo-product-inquiry="{esc(p["sku"])}" href="{esc(inquiry(key))}">Ask about {esc(p["sku"])} →</a></article>')
    return '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:18px">'+''.join(out)+'</div>'

def main():
    body=(ROOT/'scripts/data/visual-sourcing-body.html').read_text().replace('<!-- product-references -->',cards()).replace('PHOTO_INQUIRY',esc(inquiry()))
    p=PRODUCTS['rw26801']
    build(dict(slug=SLUG,title='Find Craft Supplies from a Photo | Qula Craft',h1='Find the Craft Components in Your Reference Photo',desc='Turn a bag charm, decoden or slime reference photo into a component list. Compare actual Qula SKUs, dimensions, attachment checks and bulk packing.',crumb='Photo to components',eyebrow='Visual Sourcing · DIY Components',updated='November 10, 2026',datePublished='2026-11-10',dateModified='2026-11-10',answer='Start with a full project photo and a close-up of the part you want. Identify the decorative pieces, connectors and base separately, then compare catalog references by size, material, backing and packing. Qula Craft accepts reference-photo inquiries; an exact match, sample, custom design or finished assembly needs confirmation.',hero=p['imagesLocal'][0],heroAlt='RW26801 miniature white and yellow fried-egg resin decorations',heroCap='Original RW26801 product photograph. See the component references below; the page does not show a supplied finished kit.',bodyHtml=body,note='The pictured references are separate catalog products, not a preassembled kit. Pack references are not minimum orders. Images do not establish exact color, size, material or assembly compatibility.',ctaH2='Have the picture but not the product names?',ctaP='Attach your reference and identify the parts you want to source. Include the quantity, destination and what must match. We can review existing product references and any development request before quoting.',ctaHref=inquiry(),ctaLabel='Send a reference-photo inquiry',faq=[('Can you identify every material from a photo?','A photo can guide visual selection but cannot establish composition, dimensions or compatibility. Confirm those details against the selected product record and sample.'),('Can I buy only the components in a finished-project photo?','Mark the components required and list bases, hardware and packaging separately. Availability and any finished assembly are reviewed in the quotation.'),('Can you guarantee an exact match to my reference?','No exact match is established by a reference photo. Compare available catalog options or discuss a custom brief and sample approval.')],related=[('guide-decoden-supplies.html','Plan a decoden layout','Compare component size, backing and fixing method.'),('guide-beadable-pen-beads.html','Choose beads and check fit','Confirm hole, direction and occupied length.'),('guide-samples-and-inspection.html','Approve the actual sample','Record the selected reference and acceptance criteria.')]))
    path=ROOT/SLUG; text=path.read_text().replace(' &mdash; the people who quote and pack these lines every week.','.')
    # Reuse the site's reviewed organization identities rather than the legacy
    # guide builder's inline Organization placeholders.
    shell=(ROOT/'guide-slime-business-supply-checklist.html').read_text()
    identities=[]
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',shell,re.S):
        node=json.loads(raw)
        if node.get('@type') in ('Organization','WebSite'): identities.append(node)
    def schema(match):
        node=json.loads(match[1])
        if node.get('@type')=='FAQPage': return ''
        if node.get('@type')=='Article':
            node['author']={'@id':BASE+'#organization'}
            node['publisher']={'@id':BASE+'#organization'}
        return '<script type="application/ld+json">'+json.dumps(node,ensure_ascii=False)+'</script>'
    text=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,text,flags=re.S)
    text=text.replace('</head>',''.join('<script type="application/ld+json">'+json.dumps(x,ensure_ascii=False)+'</script>' for x in identities)+'</head>')
    path.write_text(text)
    marker='<!-- photo-sourcing:start -->'; end='<!-- photo-sourcing:end -->'
    card=marker+f'<article class="article-card"><span>Photo to Components</span><h3>Find Craft Supplies from a Reference Photo</h3><p>Identify pictured parts, compare real product photos and build a quantity-by-SKU inquiry.</p><a href="{SLUG}">Find the components →</a></article>'+end
    resources=ROOT/'resources.html'; text=resources.read_text(); text=re.sub(re.escape(marker)+'.*?'+re.escape(end),'',text,flags=re.S);text=text.replace('<div class="article-grid">','<div class="article-grid">'+card,1);text=text.replace('16 sourcing guides written from the questions buyers actually send us','Practical sourcing guides covering buyer questions');resources.write_text(text)
    for name in ['index.html','resin-charms.html','polymer-clay-sprinkles.html','keychain.html','applications.html']:
        path=ROOT/name;text=path.read_text();text=re.sub(r'<!-- photo-entry:start -->.*?<!-- photo-entry:end -->','',text,flags=re.S)
        entry=f'<!-- photo-entry:start --><div class="container" style="padding:16px 20px"><p><strong>Have a photo instead of a product name?</strong> <a href="{SLUG}">Identify the parts and compare actual products →</a></p></div><!-- photo-entry:end -->'
        if 'class="buyer-questions"' in text:
            pos=text.index('<section class="buyer-questions"');text=text[:pos]+entry+text[pos:]
        else:
            pos=text.index('</section>',text.index('<main'))+len('</section>');text=text[:pos]+entry+text[pos:]
        path.write_text(text)
    # One concise answer above the product grid; preserve the existing detailed
    # buying answers and product-first browsing below it.
    path=ROOT/'resin-charms.html';text=path.read_text();text=re.sub(r'<!-- quick-buying-answer:start -->.*?<!-- quick-buying-answer:end -->','',text,flags=re.S)
    entry='<div class="container" style="padding:0 20px 16px"><p><strong>Planning 1,000 pieces?</strong> For a SKU confirmed at 100 pieces per bag, that is 10 bags before spare allowance. A standard random mix does not guarantee selected designs. <a href="guide-find-craft-supplies-from-photo.html#quantity-plan">Build a component and quantity plan →</a></p></div>'
    pos=text.index('<section class="buyer-questions"');text=text[:pos]+'<!-- quick-buying-answer:start -->'+entry+'<!-- quick-buying-answer:end -->'+text[pos:];path.write_text(text)
    sitemap=ROOT/'sitemap.xml';text=sitemap.read_text();url=BASE+SLUG
    text=re.sub(r'\n?<url>\s*<loc>'+re.escape(url)+r'</loc>.*?</url>\n?','',text,flags=re.S)
    for changed in ['', 'resources.html', 'resin-charms.html', 'polymer-clay-sprinkles.html', 'keychain.html', 'applications.html']:
        def update_date(match):
            block=match[0]
            if '<lastmod>' in block: return re.sub(r'<lastmod>.*?</lastmod>', '<lastmod>2026-11-10</lastmod>', block)
            return block.replace('</loc>', '</loc><lastmod>2026-11-10</lastmod>', 1)
        text=re.sub(r'<url>\s*<loc>'+re.escape(BASE+changed)+r'</loc>.*?</url>', update_date, text, flags=re.S)
    text=re.sub(r'\s*</urlset>\s*$', '\n</urlset>\n', text)
    images=''.join(f'<image:image><image:loc>{BASE+PRODUCTS[k]["imagesLocal"][0]}</image:loc></image:image>' for k,*_ in SELECTION)
    text=text.replace('</urlset>',f'<url><loc>{url}</loc><lastmod>2026-11-10</lastmod>{images}</url>\n</urlset>');sitemap.write_text(text)
    print('Built photo sourcing guide, source-photo references and discovery links')

if __name__=='__main__': main()
