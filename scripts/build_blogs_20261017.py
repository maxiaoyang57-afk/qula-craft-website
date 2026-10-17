"""Publish two source-backed application articles without rebuilding existing pages."""
from pathlib import Path
import html, json, re
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.qulacrafts.com/'
DATE = '2026-10-17'
esc = lambda value: html.escape(str(value), quote=True)
articles = json.loads((ROOT / 'scripts/data/blogs-20261017.json').read_text())
catalog = json.loads((ROOT / 'assets/data/product-catalog.json').read_text())
products = {p['sku']: p for c in catalog['categories'] for p in c['products']}
shell = (ROOT / 'guide-decoden-supplies.html').read_text()
pre = shell[:re.search(r'<main[^>]*>', shell).end()]
pre = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', '', pre, flags=re.S)
post = shell[shell.index('</main>'):]
adobe = 'https://color.adobe.com/create/color-wheel'
adhesive = 'https://ilovetocreate.com/pages/faqs'

def figure(sku, caption):
    p = products[sku]
    w, h = Image.open(ROOT / p['image']).size
    return f'<figure style="margin:28px 0"><a href="{p["pdp"]}"><img src="{p["image"]}" width="{w}" height="{h}" loading="lazy" alt="{esc(p.get("titleFull",p["title"]))}" style="display:block;width:min(100%,560px);height:auto;object-fit:contain;margin:auto;border-radius:18px"></a><figcaption class="small-note" style="margin-top:10px">{esc(caption)} <a href="{p["pdp"]}">View {sku} details →</a></figcaption></figure>'

for a in articles:
    url = BASE + a['slug']
    cover = BASE + products[a['heroSku']]['image']
    head = pre
    head = re.sub(r'<title>.*?</title>', '<title>'+esc(a['title'])+'</title>', head, count=1, flags=re.S)
    values = {'description':a['description'], 'og:title':a['title'], 'twitter:title':a['title'], 'og:description':a['description'], 'twitter:description':a['description'], 'og:url':url, 'og:image':cover, 'twitter:image':cover}
    for name,value in values.items():
        head = re.sub(r'(<meta (?:name|property)="'+re.escape(name)+r'" content=")[^"]*(")', lambda m:m[1]+esc(value)+m[2], head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m:m[1]+url+m[2], head)
    head = re.sub(r'(hreflang="[^"]*" href=")[^"]*(")',lambda m:m[1]+url+m[2],head)
    head = re.sub(r'\s*<meta property="og:image:(?:width|height|type)"[^>]*>', '', head)
    article = {'@context':'https://schema.org','@type':'BlogPosting','headline':a['title'],'description':a['description'],'image':cover,'datePublished':DATE,'dateModified':DATE,'mainEntityOfPage':url,'author':{'@type':'Organization','name':'Qula Craft','url':BASE,'logo':BASE+'assets/images/favicon.png'},'publisher':{'@type':'Organization','@id':BASE+'#organization','name':'Qula Craft','logo':{'@type':'ImageObject','url':BASE+'assets/images/favicon.png'}}}
    crumbs = {'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':name,'item':href} for i,(name,href) in enumerate([('Home',BASE),('Resources',BASE+'resources.html'),(a['title'],url)])]}
    head = head.replace('</head>', ''.join('<script type="application/ld+json">'+json.dumps(o)+'</script>\n' for o in [article,crumbs])+'</head>')
    body = f'<section class="page-hero"><div class="container narrow"><nav class="breadcrumb"><a href="index.html">Home</a> / <a href="resources.html">Resources</a> / <span>{esc(a["eyebrow"])}</span></nav><span class="eyebrow">{esc(a["eyebrow"])}</span><h1>{esc(a["title"])}</h1><p class="small-note">Published October 17, 2026 · Qula Craft</p></div></section><section class="section" style="padding-top:26px"><article class="container guide-body"><div class="answer-box">{esc(a["answer"])}</div>'
    body += figure(a['heroSku'],a['heroCaption'])
    for i,(heading,*paragraphs) in enumerate(a['sections']):
        body += f'<section id="step-{i+1}"><h2>{esc(heading)}</h2>'+''.join('<p>'+esc(p)+'</p>' for p in paragraphs)
        if 'palette' in heading.lower() or 'color from samples' in heading.lower():
            body += f'<p class="small-note">Palette planning reference: <a href="{adobe}" target="_blank" rel="noopener">Adobe Color wheel</a>.</p>'
        if 'fixing method' in heading.lower() or 'bonding' in heading.lower():
            body += f'<p class="small-note">Surface-selection reference: <a href="{adhesive}" target="_blank" rel="noopener">Aleene’s manufacturer FAQ, Glues &amp; Adhesives</a>. Follow the instructions for your selected product.</p>'
        body += '</section>'
        if i==1:
            body += '<div class="guide-note"><strong>Compare the components</strong><ul>'+''.join(f'<li><a href="{products[s]["pdp"]}">{s}: {esc(products[s].get("titleFull",products[s]["title"]))}</a></li>' for s in a['products'])+'</ul></div>'
        if i==2:
            sku = a['products'][1]
            body += figure(sku,'Compare the actual component footprint and back shape before fixing the layout.')
    body += '<h2>Build your own component shortlist</h2><p>Send your project image, selected product codes, quantities and packing preference so we can discuss the available options.</p><p><a class="btn btn-primary" href="quote.html">Ask about these craft components →</a></p></article></section><section class="section section-soft"><div class="container guide-body"><h2>Keep exploring</h2><div class="article-grid">'
    body += ''.join(f'<article class="article-card"><span>Related guide</span><h3><a href="{href}">{esc(label)}</a></h3><a class="text-link" href="{href}">Read guide →</a></article>' for href,label in a['related'])+'</div></div></section>'
    (ROOT/a['slug']).write_text(head+body+post)
    print(a['slug'],len(re.findall(r'\b[A-Za-z]+\b',re.sub('<[^>]*>',' ',body))),'words')

hub = ROOT/'resources.html'
raw = hub.read_text()
cards = ''.join(f'<article class="article-card"><span>{esc(a["eyebrow"])}</span><h3>{esc(a["title"])}</h3><p>{esc(a["description"])}</p><a href="{a["slug"]}">Read the project guide →</a></article>' for a in articles if f'href="{a["slug"]}"' not in raw)
raw = raw.replace('<div class="article-grid">','<div class="article-grid">'+cards,1)
hub.write_text(raw)
for name in ['llms.txt','llms-full.txt']:
    f=ROOT/name; raw=f.read_text()
    for a in articles:
        if BASE+a['slug'] not in raw: raw+='\n- ['+a['title']+']('+BASE+a['slug']+'): '+a['description']+'\n'
    f.write_text(raw)
f=ROOT/'sitemap.xml'; raw=f.read_text()
for a in articles:
    if BASE+a['slug'] not in raw: raw=raw.replace('</urlset>',f'<url><loc>{BASE+a["slug"]}</loc><lastmod>{DATE}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n</urlset>')
raw=re.sub(r'(<loc>'+re.escape(BASE+'resources.html')+r'</loc>\s*<lastmod>)[^<]+',r'\g<1>'+DATE,raw)
f.write_text(raw)
