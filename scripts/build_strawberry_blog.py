"""Build the strawberry project article and its narrow discovery links."""
import html, json, re
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.qulacrafts.com/'
SLUG = 'blog-strawberry-polymer-clay-slices.html'
TITLE = 'Strawberry Polymer Clay Slices: 3 DIY Ideas | QULA'
H1 = 'Strawberry Polymer Clay Slices for Slime, Cards and Gifts'
DESCRIPTION = 'Try strawberry polymer clay slices in slime, shaker cards and gift tags. Compare pink and red designs, matching leaves, sizes and packing with QULA.'
DATE = '2026-11-09'
CATALOG = json.loads((ROOT/'assets/data/product-catalog.json').read_text())
PRODUCTS = {p['sku']: p for c in CATALOG['categories'] for p in c['products']}
FACTS = {
 'YX693': ('Pink strawberry slices', '5 mm', 'Pale pink berries, light green caps and cream-white dots.'),
 'YX318': ('Strawberry cross-section slices', 'Approximately 5 mm', 'Red outlines, green caps and white-and-pink centers.'),
 'YX329': ('Green leaf slices', '5 mm', 'Light green leaves with pale branching veins.'),
 'YX241': ('Daisy flower discs', '5 mm', 'Colored discs with white petals and yellow centers.')
}
esc = lambda s: html.escape(str(s), quote=True)
def quote(sku=None):
 p = PRODUCTS[sku] if sku else None
 values = dict(source='strawberry-projects', entry_page='/'+SLUG,
               category='Polymer Clay Sprinkles',
               application=('Strawberry DIY; item: '+BASE+p['pdp']) if p else 'Strawberry craft project: samples, sizes, packing and quotation')
 if p: values.update(sku=sku,product=p['title'],image=p['image'])
 else: values.update(product='Polymer Clay Sprinkles',image='assets/images/category-covers-v2/polymer-clay-slices-cover-v2.webp')
 return 'quote.html?'+urlencode(values)
def card(sku):
 p=PRODUCTS[sku];label,size,detail=FACTS[sku]
 return f'''<article class="strawberry-product" data-strawberry-sku="{sku}"><a href="{p['pdp']}"><img src="{p['image']}" width="{p['imageWidth']}" height="{p['imageHeight']}" alt="{esc(p['imageAlt'])}" loading="lazy" decoding="async"></a><div><span class="eyebrow">{sku}</span><h3><a href="{p['pdp']}">{esc(label)}</a></h3><p>{esc(detail)}</p><dl><dt>Listed size</dt><dd>{esc(size)}</dd><dt>Reference pack</dt><dd>500 g/bag</dd></dl><a class="text-link" href="{p['pdp']}">View {sku} details →</a><a class="btn btn-primary" data-strawberry-quote="{sku}" href="{esc(quote(sku))}">Ask about {sku}</a></div></article>'''

BODY = '''<section class="page-hero"><div class="container narrow"><nav class="breadcrumb"><a href="index.html">Home</a> / <a href="resources.html">Resources</a> / <span>Strawberry Slice Projects</span></nav><span class="eyebrow">DIY Projects · Polymer Clay Slices</span><h1>Strawberry Polymer Clay Slices for Slime, Cards and Gifts</h1><p>A pink berry, a red cross-section, a leaf or a daisy: choose a few small pieces around the thing you want to make.</p><p class="small-note">November 9, 2026 · Qula Craft</p></div></section>
<section class="section" style="padding-top:24px"><article class="container guide-body strawberry-guide">
<div class="answer-box"><strong>What can you make with strawberry polymer clay slices?</strong> These non-edible decorative pieces can be used to plan strawberry-themed slime toppings, shaker cards and gift tags. The two strawberry designs below have different colors and outlines. Try a sample against your project, especially where thickness or contact with slime matters.</div>
<p>A strawberry tag can work with just one berry beside a handwritten name. A shaker card has room for a few loose pieces behind its window. A slime collection needs a design that still shows clearly beside the jar and label. Start there, before choosing a whole bag of matching extras.</p>
<nav class="strawberry-nav" aria-label="Strawberry project sections"><a href="#choose">Choose a design</a><a href="#slime">Slime toppings</a><a href="#shaker-cards">Shaker cards</a><a href="#gift-tags">Gift tags</a><a href="#questions">Buyer questions</a></nav>
<section id="choose"><h2>Pink strawberries or red cross-sections?</h2><p>YX693 has a pale pink body, cream-white dots and a light green cap. It is an easy starting point for a soft pink card or a pastel gift label. YX318 shows the inside of a strawberry: a red edge around a white-and-pink center, with a green cap at the top. Try that design beside a red label or a summer fruit illustration.</p><p>The listed size is 5 mm for YX693 and approximately 5 mm for YX318. That does not make them interchangeable in a tight space. Lay the actual pieces on your printed design and ask about thickness if they need to sit inside a window or under a finish.</p><div class="strawberry-products">[[YX693]][[YX318]]</div><p class="small-note">Original product photographs. The nail tip and photographed container are presentation references, supplied separately from the decorative slices.</p></section>
<section id="slime"><h2>1. Build the strawberry theme around the slime jar</h2><p>Put a few sample berries beside the jar, lid and label. The red YX318 design gives you a clear fruit motif; pink YX693 follows a quieter palette. Pick one as the main strawberry, then see whether a few leaves or daisies add anything. You may find the berry alone is enough.</p><p>For strawberry sprinkles used in slime, test every selected component in your own formula. Keep a note of the amount added, take a photo at the start, and review the texture, appearance and any color transfer over the period relevant to your product. A result in one formula does not establish the same result in another.</p><p>You can also compare a topped jar with a separate decoration packet. Decide the packet quantity from your own trial rather than copying a dose from another product. The <a href="guide-clay-slices-vs-resin-charms-slime.html">clay slices and resin charms guide</a> covers further material choices for slime.</p></section>
<section id="shaker-cards"><h2>2. Leave room for the pieces to move in a shaker card</h2><p>Try pink YX693 beside a few YX241 daisies for a strawberry garden card. For a red fruit-patch design, place YX318 beside YX329 leaves. Keep the greeting visible and use the window as a frame for the small shapes.</p><p>Before sealing the card, check the thickest piece against the space inside the window. Move the card gently and watch whether the shapes travel freely or catch at an edge. Adding more filler can hide the artwork and leave less room for movement, so start with a sparse arrangement.</p><p>Here are the two supporting motifs from the catalog. They are separate products, so list the codes separately if you want to discuss a combined assortment.</p><div class="strawberry-products">[[YX329]][[YX241]]</div></section>
<section id="gift-tags"><h2>3. Put a strawberry beside the message on a gift tag</h2><p>Write the name first. Set one berry near a corner, turn a leaf toward it, and leave the rest of the tag clear. A single daisy can repeat a color from the wrapping paper without crowding the message.</p><p>Arrange the actual pieces on the card before fixing them. Choose an adhesive for the two surfaces and follow its instructions. These slices are not listed as self-adhesive, and fixing materials are separate. If the tag will go into an envelope, check that the raised decoration has room and protection.</p><p>For a workshop or DIY kit, make one complete example and count what it uses. Keep berries, leaves and flowers identifiable while you portion the components. That makes it easier to replace a design or explain what belongs in each packet. Use the <a href="guide-diy-craft-kit-components.html">craft kit planning guide</a> for the rest of the pack.</p></section>
<section id="packing"><h2>How much should you order for a small collection?</h2><p>All four catalog references list 500 g per bag. Weight alone does not tell you how many berries, leaves or daisies are inside. If your kit calls for a fixed number of pieces, count a sample before estimating the order.</p><p>For weight-based repacking, 500 g divided into 10 g portions gives 50 portions before handling loss. That is a calculation example, not a ready-made retail pack or a suggested slime dose. Try filling the actual packet, allow for your packing process, and ask for a quotation using clear units.</p><p>The listed bag weight is not the minimum order. Current availability, MOQ, sample charges, any combined mix and delivery arrangements are confirmed with the selected SKUs. The <a href="guide-polymer-clay-sprinkles-bulk.html">bulk sprinkle buying guide</a> explains the wider sourcing checks.</p></section>
<section id="questions"><h2>A few questions before choosing the slices</h2><h3>Are the strawberry sprinkles edible?</h3><p>No. They are decorative craft components. Keep that description clear on the finished pack, particularly when a fruit or dessert theme could cause confusion.</p><h3>Can these pieces be used for nail art?</h3><p>Compare the selected sample with the nail area and intended finish. You need the thickness and a suitable attachment method as well as the listed size; a styling photo cannot establish fit on its own.</p><h3>Can I buy strawberries, leaves and daisies together?</h3><p>Send the product codes and describe the proportions you would like. The four references here are separate catalog items. A custom mix needs an availability and packing review before it can be quoted.</p></section>
<div class="guide-note"><h2>Choose the pieces for your strawberry project</h2><p>Start with YX693 or YX318, then add a leaf or daisy only if the layout needs it. Send the codes, intended use, quantity and unit, packing needs and destination. Include any thickness or sample question you need answered.</p><p><a href="polymer-clay-sprinkles.html">Browse all polymer clay slices and sprinkles</a></p><a class="btn btn-primary" data-strawberry-project-inquiry href="[[QUOTE]]">Ask about samples and packing</a></div>
</article></section>'''
for sku in FACTS: BODY=BODY.replace('[['+sku+']]',card(sku))
BODY=BODY.replace('[[QUOTE]]',esc(quote()))
shell=(ROOT/'guide-diy-craft-kit-components.html').read_text()
head=shell[:re.search(r'<main[^>]*>',shell).end()]
head=re.sub(r'<script type="application/ld\+json">.*?</script>\s*','',head,flags=re.S)
head=re.sub(r'<title>.*?</title>','<title>'+esc(TITLE)+'</title>',head,count=1,flags=re.S)
url=BASE+SLUG;cover=BASE+PRODUCTS['YX693']['image']
for name,value in {'description':DESCRIPTION,'og:title':TITLE,'og:description':DESCRIPTION,'og:url':url,'og:image':cover,'twitter:title':TITLE,'twitter:description':DESCRIPTION,'twitter:image':cover}.items():
 pattern=r'(<meta (?:name|property)="'+re.escape(name)+r'" content=")[^"]*(")'
 if re.search(pattern,head):head=re.sub(pattern,lambda m:m[1]+esc(value)+m[2],head)
 elif name.startswith('twitter:'):head=head.replace('</head>',f'<meta name="{name}" content="{esc(value)}">\n</head>')
head=re.sub(r'(<link rel="canonical" href=")[^"]*(")',lambda m:m[1]+url+m[2],head)
head=re.sub(r'(hreflang="[^"]*" href=")[^"]*(")',lambda m:m[1]+url+m[2],head)
head=head.replace('</head>','<link rel="stylesheet" href="assets/css/strawberry-guide.css?v=20261109">\n</head>')
article={'@context':'https://schema.org','@type':'Article','headline':H1,'description':DESCRIPTION,'image':cover,'datePublished':DATE,'dateModified':DATE,'mainEntityOfPage':url,'inLanguage':'en','author':{'@type':'Organization','@id':BASE+'#organization','name':'Qula Craft','url':BASE,'logo':BASE+'assets/images/favicon.png'},'publisher':{'@type':'Organization','name':'Qula Craft','logo':{'@type':'ImageObject','url':BASE+'assets/images/favicon.png'}}}
crumb={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':name,'item':link}for i,(name,link)in enumerate([('Home',BASE),('Resources',BASE+'resources.html'),(H1,url)])]}
head=head.replace('</head>',''.join('<script type="application/ld+json">'+json.dumps(s,ensure_ascii=False).replace('<','\\u003c')+'</script>\n'for s in [article,crumb])+'</head>')
(ROOT/SLUG).write_text(head+BODY+shell[shell.index('</main>'):])
marker='strawberry-blog'
p=ROOT/'resources.html';s=p.read_text();s=re.sub(r'<!-- '+marker+r':start -->.*?<!-- '+marker+r':end -->','',s,flags=re.S)
entry=f'<!-- {marker}:start --><article class="article-card"><span>DIY Projects · Strawberry Slices</span><h3>{H1}</h3><p>Try pink or red berries with leaves and daisies for slime, shaker cards and gift tags. Compare four real product references.</p><a href="{SLUG}">Read the strawberry project guide →</a></article><!-- {marker}:end -->'
assert '<div class="article-grid">'in s;s=s.replace('<div class="article-grid">','<div class="article-grid">'+entry,1);p.write_text(s)
p=ROOT/'polymer-clay-sprinkles.html';s=p.read_text();s=re.sub(r'<!-- '+marker+r':start -->.*?<!-- '+marker+r':end -->','',s,flags=re.S)
start=s.index('href="guide-diy-craft-kit-components.html"');end=s.index('</ul>',start)
s=s[:end]+f'<!-- {marker}:start --><li><a href="{SLUG}">Strawberry slice projects</a> — choose pink or red berries for slime, shaker cards and gift tags.</li><!-- {marker}:end -->'+s[end:];p.write_text(s)
p=ROOT/'llms.txt';s=p.read_text();line=f'- [{H1}]({url}): Four strawberry, leaf and daisy catalog references, project layouts and packing questions.'
s='\n'.join(x for x in s.splitlines()if SLUG not in x).rstrip()+'\n\n'+line+'\n';p.write_text(s)
p=ROOT/'sitemap.xml';s=p.read_text()
if url not in s:s=s.replace('</urlset>',f'  <url><loc>{url}</loc><lastmod>{DATE}</lastmod></url>\n</urlset>')
for changed in ['resources.html','polymer-clay-sprinkles.html']:
 pattern=r'(<url>\s*<loc>'+re.escape(BASE+changed)+r'</loc>\s*<lastmod>)[^<]+(</lastmod>)'
 s,n=re.subn(pattern,lambda m:m[1]+DATE+m[2],s);assert n==1,changed
p.write_text(s)
print('Built strawberry article and two inbound entries; product data unchanged.')
