"""Build the requested family gift article using the current public guide shell."""
import html,json,re
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BASE='https://www.qulacrafts.com/'
a=json.loads((ROOT/'scripts/data/christmas-family-gifts-20261105.json').read_text())
products={p['sku']:p for c in json.loads((ROOT/'assets/data/product-catalog.json').read_text())['categories'] for p in c['products']}
esc=lambda v:html.escape(str(v),quote=True)
shell=(ROOT/'blog-candy-decoden-layout.html').read_text()
head=shell[:re.search(r'<main[^>]*>',shell).end()]
head=re.sub(r'<script type="application/ld\+json">.*?</script>\s*','',head,flags=re.S)
head=re.sub(r'<title>.*?</title>','<title>'+esc(a['title'])+'</title>',head,count=1,flags=re.S)
url=BASE+a['slug']; cover=BASE+products[a['heroSku']]['image']
for n,v in {'description':a['description'],'og:title':a['title'],'og:description':a['description'],'og:image':cover,'og:url':url,'twitter:image':cover}.items():
 head=re.sub(r'(<meta (?:name|property)="'+re.escape(n)+r'" content=")[^"]*(")',lambda m:m[1]+esc(v)+m[2],head)
head=re.sub(r'(<link rel="canonical" href=")[^"]*(")',lambda m:m[1]+url+m[2],head)
head=re.sub(r'(hreflang="[^"]*" href=")[^"]*(")',lambda m:m[1]+url+m[2],head)
schema={'@context':'https://schema.org','@type':'BlogPosting','headline':a['headline'],'description':a['description'],'image':cover,'datePublished':a['date'],'dateModified':a['date'],'mainEntityOfPage':url,'author':{'@type':'Organization','name':'Qula Craft','url':BASE,'logo':BASE+'assets/images/favicon.png'},'publisher':{'@type':'Organization','name':'Qula Craft','logo':{'@type':'ImageObject','url':BASE+'assets/images/favicon.png'}}}
crumbs={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':n,'item':u} for i,(n,u) in enumerate([('Home',BASE),('Resources',BASE+'resources.html'),(a['headline'],url)])]}
head=head.replace('</head>',''.join('<script type="application/ld+json">'+json.dumps(s)+'</script>\n' for s in [schema,crumbs])+'</head>')
def figure(sku,caption,eager=False):
 p=products[sku];w,h=Image.open(ROOT/p['image']).size
 return f'<figure style="margin:28px 0"><a href="{p["pdp"]}"><img src="{p["image"]}" width="{w}" height="{h}" loading="{"eager" if eager else "lazy"}" alt="{esc(p["title"])}" style="display:block;width:min(100%,520px);height:auto;object-fit:contain;margin:auto;border-radius:18px"></a><figcaption class="small-note" style="margin-top:10px">{esc(caption)} <a href="{p["pdp"]}">View {sku} →</a></figcaption></figure>'
body='<section class="page-hero"><div class="container narrow"><nav class="breadcrumb"><a href="index.html">Home</a> / <a href="resources.html">Resources</a> / Christmas Family DIY</nav><span class="eyebrow">'+esc(a['eyebrow'])+'</span><h1>'+esc(a['headline'])+'</h1><p>DIY gifts to make together with resin charms and polymer clay slices.</p><p class="small-note">Published November 5, 2026 · Qula Craft</p></div></section><section class="section" style="padding-top:26px"><article class="container guide-body"><p>'+esc(a['introduction'])+'</p>'
body+=figure(a['heroSku'],a['heroCaption'],True)
body+='<nav class="guide-note" aria-label="Christmas gift ideas"><strong>Choose a project</strong><ul>'+''.join('<li><a href="#'+x['id']+'">'+esc(x['heading'])+'</a></li>' for x in a['sections'][2:6])+'</ul></nav>'
for i,x in enumerate(a['sections']):
 body+='<section id="'+x['id']+'"><h2>'+esc(x['heading'])+'</h2>'+''.join('<p>'+esc(p)+'</p>' for p in x['paragraphs'])+'</section>'
 if i==1:body+='<p>Explore <a href="resin-charms.html">resin charms and flatback cabochons</a> and <a href="polymer-clay-sprinkles.html">polymer clay slices and sprinkles</a> before choosing your components.</p>'
 if i==3:body+=figure('YX4108','A Christmas polymer clay slice assortment can suggest a palette. Confirm the designs and packing for your selected SKU; the project layout is your own.')
body+='<section id="supplies"><h2>'+esc(a['sourcingHeading'])+'</h2>'+''.join('<p>'+esc(p)+'</p>' for p in a['sourcingParagraphs'][:1])+'<p>Browse <a href="resin-charms.html">Qula Craft resin charms</a> and <a href="polymer-clay-sprinkles.html">polymer clay slices</a>, or explore <a href="https://www.haibucrafts.com/products/resin-charms-for-slime/">HAIBU resin components</a> and <a href="https://www.haibucrafts.com/products/polymer-clay-slices-wholesale/">polymer clay supplies</a>.</p><p>'+esc(a['sourcingParagraphs'][1])+'</p><p><a class="btn btn-primary" href="quote.html?product=Christmas%20Family%20DIY%20Gift%20Components&amp;category=Resin%20Charms">Discuss Christmas craft components →</a></p><p>'+esc(a['sourcingParagraphs'][2])+'</p></section>'
body+='<aside class="guide-note"><strong>Keep creating</strong><ul><li><a href="guide-diy-craft-kit-components.html">Plan the components for a DIY craft kit</a></li><li><a href="guide-decoden-supplies.html">Choose resin charms and decorative details</a></li><li><a href="https://www.haibucrafts.com/blog/christmas-family-diy-gift-materials/">HAIBU: prepare materials for a Christmas family craft activity</a></li></ul></aside></article></section>'
(ROOT/a['slug']).write_text(head+body+shell[shell.index('</main>'):])
p=ROOT/'resources.html';s=p.read_text();card='<article class="article-card"><span>Christmas Family DIY</span><h3>'+esc(a['headline'])+'</h3><p>'+esc(a['description'])+'</p><a href="'+a['slug']+'">Make Christmas gifts together →</a></article>'
if 'href="'+a['slug']+'"' not in s:s=s.replace('<div class="article-grid">','<div class="article-grid">'+card,1)
p.write_text(s)
for name in ['llms.txt','llms-full.txt']:
 p=ROOT/name;s=p.read_text()
 if url not in s:s+='\n- ['+a['headline']+']('+url+'): '+a['description']+'\n'
 p.write_text(s)
p=ROOT/'sitemap.xml';s=p.read_text()
if url not in s:s=s.replace('</urlset>',f'<url><loc>{url}</loc><lastmod>{a["date"]}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n</urlset>')
s=re.sub(r'(<loc>'+re.escape(BASE+'resources.html')+r'</loc>\s*<lastmod>)[^<]+',lambda m:m[1]+a['date'],s)
p.write_text(s)
print('Built',a['slug'])
