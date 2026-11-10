"""Build the QULA bulk keychain guide from published SKU facts."""
import html
import json
import re
from pathlib import Path
from urllib.parse import urlencode
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.qulacrafts.com/'
SLUG = 'guide-buy-keychains-in-bulk.html'
TITLE = 'Where to Buy Keychains in Bulk: Buyer Guide | QULA'
H1 = 'Where to Buy Keychains in Bulk: Finished Styles & DIY Supplies'
DESC = 'Compare finished keychains, bag charms and DIY supplies by real SKU, material, size and pack. Prepare a sample shortlist and request a QULA wholesale quote.'
DATE = '2026-11-10'
DATA = json.loads((ROOT/'assets/data/pdp-data.json').read_text())
CATALOG = json.loads((ROOT/'assets/data/product-catalog.json').read_text())
PRODUCTS = {p['sku']: p for c in CATALOG['categories'] for p in c['products']}
FACTS = {p['sku']: p for p in DATA}
SELECTION = [
    ('CDK001890', 'Fruit resin keychains', 'A finished-style reference for a fruit collection. Confirm the selected fruit designs and the hardware supplied.'),
    ('CDK26017', 'Tree charms with lobster clasps', 'A clasped reference to compare for a bag-charm display. Check the selected tree design and the usable clasp opening.'),
    ('CDK070', 'Colorful split key rings', 'Hardware only. List the charm, connector and any chain separately when planning an assembly.'),
    ('YA425', 'Heart acrylic beads', 'A component for a proposed threaded layout. Compare the listed hole with the actual cord or hardware; test the assembly first.'),
]
esc = lambda x: html.escape(str(x), quote=True)

def quote(sku=None):
    values = {'source': 'bulk-keychain-guide', 'entry_page': '/'+SLUG,
              'application': 'Wholesale keychain or bag charm project: selected design, quantity, packing and sample requirements'}
    if sku:
        p=PRODUCTS[sku]
        category = {'Plastic Beads': 'Acrylic Beads', 'Keychain': 'Keychains'}.get(FACTS[sku]['category'], FACTS[sku]['category'])
        values.update(sku=sku, product=p['title'], image=p['image'], category=category,
                      application='Keychain project; selected catalog reference: '+BASE+p['pdp'])
    else:
        values.update(product='Keychains, bag charms and DIY supplies', category='Keychains')
    return 'quote.html?'+urlencode(values)

def card(sku, label, note):
    p=PRODUCTS[sku]; f=FACTS[sku]; specs=f['specs']
    assert specs.get('Material') and specs.get('Size'), sku
    src=p['image']; w,h=Image.open(ROOT/src).size
    rows=[('Material',specs['Material']),('Listed size',specs['Size'])]
    if specs.get('Hole diameter'): rows.append(('Listed hole',specs['Hole diameter']))
    rows.append(('Reference pack',specs.get('Standard pack') or specs['Pack reference']))
    return f'''<article class="keychain-guide-card" data-guide-sku="{esc(sku)}"><a href="{esc(p['pdp'])}"><img src="{esc(src)}" width="{w}" height="{h}" alt="{esc(p.get('imageAlt') or label+' — '+sku)}" loading="lazy" decoding="async"></a><div><span class="eyebrow">{esc(sku)}</span><h3><a href="{esc(p['pdp'])}">{esc(label)}</a></h3><dl>{''.join('<dt>'+esc(k)+'</dt><dd>'+esc(v)+'</dd>' for k,v in rows)}</dl><p>{esc(note)}</p><a class="text-link" href="{esc(p['pdp'])}">View {esc(sku)} details →</a><a class="btn btn-primary" data-guide-quote="{esc(sku)}" href="{esc(quote(sku))}">Ask about {esc(sku)}</a></div></article>'''

BODY = '''<section class="page-hero"><div class="container narrow"><nav class="breadcrumb"><a href="index.html">Home</a> / <a href="resources.html">Resources</a> / <span>Bulk Keychain Buying Guide</span></nav><span class="eyebrow">Wholesale Buying Guide · Keychains &amp; Bag Charms</span><h1>Where to Buy Keychains in Bulk: Finished Styles &amp; DIY Supplies</h1><p>Choose a finished design, a clasped bag charm or separate making supplies—and make sure the quotation covers the version you actually need.</p><p class="small-note">Updated November 10, 2026 · Qula Craft</p></div></section>
<section class="section" style="padding-top:24px"><article class="container guide-body keychain-buying-guide">
<div class="answer-box"><strong>Where can a business buy keychains in bulk?</strong> Gift wholesalers, craft-component suppliers and custom manufacturers serve different needs. For Qula Craft, start with the <a href="keychain.html">Bag Charms &amp; Keychains catalog</a> for finished-style references and hardware, or compare <a href="acrylic-beads.html">acrylic beads</a> and <a href="resin-charms.html">resin decorations</a> for a DIY project. Send exact product links and quantities for a current quotation.</div>
<p>A shop restocking a fruit keychain display needs a different order from a craft-kit business buying loose rings and beads. Both may search for “buy keychains in bulk,” but one needs an approved finished assortment while the other needs a complete component list. Decide which you are purchasing before comparing photographs or prices.</p>
<nav class="keychain-guide-nav" aria-label="Buying guide sections"><a href="#buying-route">Choose a buying route</a><a href="#compare-products">Compare real products</a><a href="#sample-check">Check samples</a><a href="#ai-sourcing">Use AI for research</a><a href="#quote-brief">Prepare an inquiry</a></nav>
<section id="buying-route"><h2>Choose a supplier for the order you need</h2><div class="keychain-table"><table><caption>Three buying routes and what to confirm</caption><thead><tr><th scope="col">Buying route</th><th scope="col">Useful when</th><th scope="col">Ask before ordering</th></tr></thead><tbody><tr><th scope="row">Finished keychains or bag charms</th><td>You want a selected design for a gift shop, collection or retail display.</td><td>Exact design, attachment, total length, assortment and packing.</td></tr><tr><th scope="row">DIY making supplies</th><td>Your team or customer assembles the item.</td><td>Every component, hole or loop, connector fit and quantity per kit.</td></tr><tr><th scope="row">Custom development</th><td>You have an original design, packaging brief or revised assembly.</td><td>Feasibility, artwork, sample stages, included parts and order-specific terms.</td></tr></tbody></table></div><p>A local keychain shop can be useful when you need to inspect one item immediately. A bulk program also needs repeat-order identification, quantities by design and a packing agreement. Ask QULA to review those requirements through <a href="customization.html">customization</a>; a reference photograph alone does not define the final supply scope.</p></section>
<section id="compare-products"><h2>Compare a finished reference with separate components</h2><p>These four catalog items illustrate different buying decisions. The dimensions and pack references below belong to each named SKU. They are separate products, not a four-part kit or a confirmed compatible assembly.</p><div class="keychain-guide-products">[[CARDS]]</div><p class="small-note">Reference packing is not the minimum order quantity. Confirm the selected option, sample availability, MOQ, price and dispatch date in the quotation.</p></section>
<section><h2>Read the size as carefully as the design</h2><p>CDK001890 lists about 35 × 78 mm. CDK26017 lists 25 × 38 mm. Before planning a display card, ask whether a listed figure describes the decoration, the body or the complete item with its attachment. For a pouch or shaker style, request both the outer dimensions and the usable internal space.</p><p>A bead's outside size does not establish how it threads. YA425 lists a 16 × 18 mm body and a 2.5 mm hole; compare that hole with the actual cord, connector or rod. CDK070 lists a 30 mm split ring, but the ring diameter does not establish whether your chosen charm can be mounted. Request the missing dimensions and assemble a sample.</p></section>
<section id="sample-check"><h2>Approve the attachment and the appearance together</h2><p>For a finished-style reference, request front and reverse photographs and check the supplied ring or clasp. Open and close the sample, check its connection to the decoration, and try it on the bag handle or key set you intend to show. Record any sharp edges, loose connections or changes you want reviewed. A product photo does not establish a load rating or durability result.</p><p>For a DIY kit, lay out all the parts and assemble one complete example. Count connectors as well as the decorative pieces. If a loose resin decoration has no confirmed hole or loop, agree on a fixing method before treating it as a hanging charm. Review sample and inspection questions in the <a href="guide-samples-and-inspection.html">sample guide</a>.</p></section>
<section><h2>Turn an assortment into a usable quantity list</h2><p>“Mixed fruit” can mean a random bag, equal quantities of chosen fruits or a specific ratio for a display. List the design codes and say whether substitution is acceptable. If a grouped listing contains several designs, name the individual component codes you want instead of relying on the first photograph.</p><p>For planning, 200 kits using one ring and two beads each would require 200 rings and 400 beads before your own spare allowance. That arithmetic is an example, not a pack offer or MOQ. A 500 g bead reference does not tell you the piece count; count and weigh an approved sample if your kits are packed by pieces. Specify whether packing is by piece, bag, set or weight.</p></section>
<section><h2>Make the custom brief specific</h2><p>For custom keychains online, separate the decorative design from the attachment and retail presentation. Send your own artwork or an authorized reference, desired dimensions, color direction, intended use and proposed quantity. State whether you want a finished item or loose components and whether cards, labels or individual bags are required.</p><p>Ask which development and sample steps apply before committing to a launch date. A digital drawing can help confirm the design direction; a physical sample is needed to review the actual scale, connection and packing. Discuss private-label presentation through <a href="private-label-packaging.html">private-label packaging</a> and confirm all charges and timing for the selected project.</p></section>
<section id="ai-sourcing"><h2>Use AI to organize a keychain sourcing shortlist</h2><p>AI assistants such as ChatGPT, Google Gemini, Microsoft Copilot, Perplexity, Claude, DeepSeek and Grok can be part of your research workflow. If your chosen tool offers web search, enable it and ask for current source links. Start with a supplier search, then compare exact product pages rather than relying on a generated product description.</p><div class="keychain-prompt"><p><strong>Supplier discovery prompt</strong></p><p>“Find wholesale suppliers of finished fruit keychains and separate keychain making supplies for a gift shop. Show the supplier website and product-page links. Separate finished items from components, and identify which dimensions, packing and order terms still need confirmation.”</p></div><div class="keychain-prompt"><p><strong>QULA catalog comparison prompt</strong></p><p>“Review qulacrafts.com for CDK001890 fruit keychains, CDK26017 tree charms, CDK070 split rings and YA425 acrylic heart beads. Cite the exact pages. Compare listed materials, dimensions, attachments and reference packing. Do not infer missing facts, a current price or compatibility between the items.”</p></div><p>The first prompt tests discovery without naming a supplier. The second helps check a known catalog. Asking an AI to open QULA does not establish that it would independently recommend QULA. Confirm the final selection with the product page, a written quotation and the sample. The tools named here are independent services; no affiliation or endorsement is implied.</p></section>
<section id="quote-brief"><h2>Send a short inquiry that can be quoted</h2><p>Include the selected SKU and product link, finished item or component requirement, quantity with its unit, intended application, packaging, destination and desired arrival date. Add any missing measurement or sample question. Keeping this on one list makes it easier to compare a revised quotation with the approved sample.</p><div class="keychain-prompt"><p><strong>Example inquiry</strong></p><p>“Please quote CDK001890 for a fruit-themed gift-shop display. Confirm the selected fruit designs, supplied attachment, complete dimensions and current packing. Quantity: [your quantity and unit]. Destination: [country]. Please advise sample options and the feasible dispatch date. Individual retail packing: [requirements].”</p></div><p><a class="btn btn-primary" href="[[QUOTE]]">Request a keychain or DIY supply quote</a></p></section>
<p>For a separate loose-decoration sourcing brief, read <a href="https://www.haibucrafts.com/blog/keychain-bag-charm-components-sourcing-guide/">HAIBU’s resin and polymer clay component guide</a>.</p><section><h2>Questions before buying bulk keychains</h2><h3>Can I buy the pictured finished assembly?</h3><p>Specify its product link and ask exactly what is included. Styling props, loose components and separately shown accessories do not automatically form a kit.</p><h3>Does a 10-piece or 100-piece pack establish the MOQ?</h3><p>No. A reference packing unit and minimum order are different facts. Confirm the MOQ for each selected design and packing option.</p><h3>Can every resin charm be attached to a key ring?</h3><p>No. Check the exact SKU for a hole, loop or agreed mounting method. An attractive front view does not establish an attachment.</p><h3>Can AI confirm a price or delivery date?</h3><p>Use the current supplier quotation for those terms. Search results and generated answers can contain older or incomplete information.</p></section>
</article></section>'''

STYLE = '''<style>.keychain-buying-guide{max-width:980px}.keychain-buying-guide section{margin:34px 0}.keychain-guide-nav{display:flex;flex-wrap:wrap;gap:10px 20px;margin:24px 0}.keychain-guide-products{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}.keychain-guide-card{min-width:0;border:1px solid #eadde3;border-radius:18px;padding:18px;background:white;display:flex;flex-direction:column}.keychain-guide-card img{width:100%;height:240px;object-fit:contain}.keychain-guide-card dl{margin:16px 0}.keychain-guide-card dt{font-weight:700}.keychain-guide-card dd{margin:0 0 10px;overflow-wrap:anywhere}.keychain-guide-card .btn{margin-top:12px;display:inline-flex}.keychain-table{overflow-x:auto}.keychain-table table{width:100%;border-collapse:collapse}.keychain-table th,.keychain-table td{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #eadde3;min-width:130px}.keychain-table caption{text-align:left;margin-bottom:12px}.keychain-prompt{padding:18px 22px;margin:18px 0;border-left:4px solid #cc3868;background:#fff5f8;border-radius:0 12px 12px 0}.keychain-prompt p{overflow-wrap:anywhere}@media(max-width:650px){.keychain-guide-products{grid-template-columns:minmax(0,1fr)}.keychain-guide-card img{height:240px}.keychain-prompt{padding:16px}}</style>'''

def build():
    shell=(ROOT/'guide-samples-and-inspection.html').read_text()
    head=shell[:re.search(r'<main[^>]*>',shell).end()]
    head=re.sub(r'<script type="application/ld\+json">.*?</script>\s*','',head,flags=re.S)
    head=re.sub(r'<title>.*?</title>','<title>'+esc(TITLE)+'</title>',head,count=1,flags=re.S)
    url=BASE+SLUG; image=BASE+PRODUCTS['CDK001890']['image']
    for name,value in [('description',DESC),('og:title',TITLE),('twitter:title',TITLE),('og:description',DESC),('twitter:description',DESC),('og:url',url),('og:image',image),('twitter:image',image)]:
        head=re.sub(r'(<meta (?:name|property)="'+re.escape(name)+r'" content=")[^"]*(")',lambda m:m[1]+esc(value)+m[2],head)
    head=re.sub(r'(<link rel="canonical" href=")[^"]*(")',lambda m:m[1]+url+m[2],head)
    head=re.sub(r'(hreflang="[^"]*" href=")[^"]*(")',lambda m:m[1]+url+m[2],head)
    article={'@context':'https://schema.org','@type':'Article','headline':H1,'description':DESC,'image':image,'datePublished':DATE,'dateModified':DATE,'mainEntityOfPage':url,'author':{'@type':'Organization','name':'Qula Craft','url':BASE,'logo':BASE+'assets/images/favicon.png'},'publisher':{'@id':BASE+'#organization'}}
    crumb={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE},{'@type':'ListItem','position':2,'name':'Resources','item':BASE+'resources.html'},{'@type':'ListItem','position':3,'name':'Bulk Keychain Buying Guide','item':url}]}
    head=head.replace('</head>',STYLE+''.join('<script type="application/ld+json">'+json.dumps(x,ensure_ascii=False).replace('<','\\u003c')+'</script>' for x in [article,crumb])+'</head>')
    body=BODY.replace('[[CARDS]]',''.join(card(*x) for x in SELECTION)).replace('[[QUOTE]]',esc(quote()))
    (ROOT/SLUG).write_text(head+body+shell[shell.index('</main>'):])
    marker='bulk-keychain-guide'
    entry=f'<article class="article-card"><span>Wholesale Buying Guide</span><h3>{esc(H1)}</h3><p>Compare finished references, rings and beads; check dimensions, samples and the exact parts included.</p><a href="{SLUG}">Read the bulk keychain buying guide →</a></article>'
    for file in ['resources.html','keychain.html']:
        p=ROOT/file;s=p.read_text();s=re.sub(r'<!-- '+marker+r':start -->.*?<!-- '+marker+r':end -->','',s,flags=re.S)
        insert='<!-- '+marker+':start -->'+entry+'<!-- '+marker+':end -->'
        if file=='resources.html':
            assert '<div class="article-grid">' in s;s=s.replace('<div class="article-grid">','<div class="article-grid">'+insert,1)
        else:
            section='<section class="section"><div class="container"><h2>Plan a bulk keychain order</h2><div class="article-grid">'+entry+'</div></div></section>'
            s=s.replace('</main>','<!-- '+marker+':start -->'+section+'<!-- '+marker+':end --></main>',1)
        p.write_text(s)
    p=ROOT/'llms.txt';s=p.read_text();s='\n'.join(l for l in s.splitlines() if SLUG not in l).rstrip()+'\n\n'+f'- [{H1}]({url}): Finished keychain versus DIY component selection, four real SKU references, sample checks and inquiry preparation.\n';p.write_text(s)
    p=ROOT/'sitemap.xml';s=p.read_text()
    if url not in s:s=s.replace('</urlset>',f'  <url><loc>{url}</loc><lastmod>{DATE}</lastmod></url>\n</urlset>')
    for file in ['resources.html','keychain.html']:
        s,n=re.subn(r'(<url>\s*<loc>'+re.escape(BASE+file)+r'</loc>\s*<lastmod>)[^<]+(</lastmod>)',lambda m:m[1]+DATE+m[2],s);assert n==1,file
    p.write_text(s)
    print('Built QULA bulk keychain guide, four SKU cards, category/resources entries and discovery links.')

if __name__=='__main__':build()
