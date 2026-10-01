"""Build the pen-sizing blog and original, dimensionally labeled SVG illustrations.

No SKU geometry or pen dimensions are inferred. The arithmetic illustration is
explicitly hypothetical. Existing page shells and brand data are preserved.
"""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.qulacrafts.com/'
SLUG = 'blog-beadable-pen-bead-size-guide.html'
ASSETS = ROOT / 'assets/images/pen-fit-guide'
ASSETS.mkdir(parents=True, exist_ok=True)

def text(x, y, value, size=21, color='#263346', weight=400, anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(value)}</text>'

def line(x1, y1, x2, y2, color='#168570', extra=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2" {extra}/>'

def dim(x1,y1,x2,y2,color='#168570'):
    return line(x1,y1,x2,y2,color,'marker-start="url(#arrow)" marker-end="url(#arrow)"')

def svg(name, height, title, desc, body):
    raw=f'''<svg xmlns="http://www.w3.org/2000/svg" width="520" height="{height}" viewBox="0 0 520 {height}" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(desc)}</desc>
<defs><marker id="arrow" viewBox="0 0 8 8" refX="4" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L8 4L0 8Z" fill="#168570"/></marker>
<linearGradient id="bead" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#ffeaf3"/><stop offset="1" stop-color="#efa8c3"/></linearGradient>
<linearGradient id="metal"><stop stop-color="#bbc9cf"/><stop offset=".48" stop-color="#fff"/><stop offset="1" stop-color="#82949d"/></linearGradient></defs>
<rect width="520" height="{height}" rx="24" fill="#fff"/><g font-family="Arial, Helvetica, sans-serif">{body}
{text(28,height-24,'Qula Craft  /  Measurement guide',16,'#657184')}
</g></svg>'''
    (ASSETS/name).write_text(raw,encoding='utf-8')

# 1: End view and side section of a generic drilled bead. No real SKU implied.
b=text(28,42,'01 / READ THE BEAD',19,'#a73561',700)+text(28,80,'Outside size is not hole size.',25,weight=700)
b+=text(28,116,'Generic shapes · not to scale',18,'#657184')
b+=text(50,161,'END VIEW',16,'#657184',700)
b+='<circle cx="150" cy="252" r="78" fill="url(#bead)" stroke="#b54e77" stroke-width="2"/><circle cx="150" cy="252" r="16" fill="#fff" stroke="#a73561" stroke-width="2"/>'
b+=dim(134,252,166,252)+line(166,252,262,224)+text(278,220,'Ød: hole',23,weight=700)+text(278,250,'diameter',21)
b+=line(72,252,72,355,'#aebfc5')+line(228,252,228,355,'#aebfc5')+dim(72,348,228,348)+text(150,384,'ØD: outside diameter',21,weight=700,anchor='middle')
b+=line(28,415,492,415,'#e5e9ef')+text(50,451,'SIDE SECTION',16,'#657184',700)
b+='<ellipse cx="150" cy="541" rx="79" ry="52" fill="url(#bead)" stroke="#b54e77" stroke-width="2"/><path d="M138 489V593H162V489" fill="#fff" stroke="#a73561" stroke-width="2"/>'
b+=line(150,468,150,614,'#82949d','stroke-dasharray="5 5"')
b+=line(168,489,269,489,'#aebfc5')+line(168,593,269,593,'#aebfc5')+dim(262,489,262,593)
b+=text(283,526,'H: stack',23,weight=700)+text(283,555,'height',23,weight=700)+text(283,588,'Along the',19)+text(283,613,'hole axis',19)
b+=text(28,652,'On shaped beads, confirm the hole direction.',19,'#657184')
svg('bead-diameter-hole-stack-height.svg',720,'Bead diameter, hole diameter and stack height','D measures the outside diameter. d measures the hole opening. H measures the occupied height along the hole axis. Generic shapes, not to scale.',b)

# 2: Generic pen and a magnified loading-path cross section.
b=text(28,42,'02 / MEASURE THE PEN',19,'#a73561',700)+text(28,80,'Two measurements to request',25,weight=700)
b+=text(28,114,'Generic pen · construction varies',18,'#657184')
b+='<rect x="108" y="161" width="70" height="52" rx="16" fill="#f3b5cb" stroke="#b54e77" stroke-width="2"/>'
b+=text(198,182,'Removable end fitting',21,weight=700)+text(198,210,'Shown detached',18,'#657184')
b+='<rect x="134" y="252" width="18" height="248" fill="url(#metal)" stroke="#82949d"/><rect x="130" y="252" width="26" height="31" fill="#c5d0d5" stroke="#82949d"/>'
for yy in range(256,283,6):b+=line(130,yy,156,yy-2,'#637984')
b+=line(118,283,359,283,'#aebfc5','stroke-dasharray="5 5"')+text(210,258,'End-stop seat',20,weight=700)
b+=text(210,311,'Position when secured',17,'#657184')
b+='<rect x="113" y="500" width="60" height="22" rx="6" fill="url(#metal)" stroke="#82949d"/><rect x="117" y="522" width="52" height="125" rx="10" fill="#ade3d3" stroke="#168570" stroke-width="2"/><path d="M117 638H169L151 676H135Z" fill="#c2d0d6" stroke="#82949d"/>'
b+=line(174,500,359,500,'#aebfc5')+dim(342,283,342,500)
b+=text(318,380,'L',34,'#168570',700,'end')+text(318,411,'Usable',20,anchor='end')+text(318,438,'bead space',20,anchor='end')
b+=text(28,531,'Lower',18)+text(28,555,'shoulder',18)
b+='<rect x="219" y="535" width="272" height="135" rx="16" fill="#f1faf7"/>'
b+=text(237,562,'ROD / LOADING PATH',15,'#168570',700)
b+='<circle cx="260" cy="605" r="22" fill="url(#metal)" stroke="#82949d"/>'
b+=dim(238,605,282,605)+text(299,601,'Ør: widest',20,weight=700)+text(299,627,'section',20,weight=700)
b+=text(28,707,'Include threads in r if beads must pass over them.',18,'#657184')
svg('pen-rod-usable-beading-length.svg',760,'Measure the pen rod and usable beading length','L is the space between the lower shoulder and upper end-stop seat in its secured position. The drawing excludes the top attachment threads from L. r is the widest part of the rod that beads must pass over. No numeric pen dimensions are asserted.',b)

# 3: Explicit hypothetical arithmetic, with axial lengths proportional in drawing.
b=text(28,42,'03 / PLAN THE STACK',19,'#a73561',700)+text(28,80,'Will the whole layout fit?',25,weight=700)
b+=text(28,116,'ILLUSTRATIVE EXAMPLE · NOT A PRODUCT SPEC',16,'#a73561',700)
b+='<rect x="102" y="174" width="16" height="300" fill="url(#metal)"/><rect x="59" y="174" width="102" height="6" fill="#fff0db" stroke="#a77935"/>'
ys=[180,282,384]
for yy in ys:
    b+=f'<ellipse cx="110" cy="{yy+45}" rx="45" ry="45" fill="url(#bead)" stroke="#b54e77" stroke-width="2"/>'
    b+=line(155,yy+45,218,yy+45,'#b6bfc9')+text(231,yy+52,'15 mm bead height',21)
for yy in [270,372]:
    b+=f'<rect x="81" y="{yy}" width="58" height="12" rx="3" fill="#ade3d3" stroke="#168570"/>'
    b+=line(140,yy+6,218,yy+6,'#b6bfc9')+text(231,yy+12,'2 mm spacer',19,'#168570')
b+=line(28,174,53,174,'#aebfc5')+line(28,474,161,474,'#aebfc5')+dim(35,174,35,474)
b+='<text x="23" y="330" transform="rotate(-90 23 330)" font-size="19" fill="#168570" text-anchor="middle">L = 50 mm</text>'
b+=line(162,177,218,160,'#a77935')+text(231,165,'1 mm remaining',19,'#936a2e')
b+='<rect x="28" y="506" width="464" height="92" rx="16" fill="#f1faf7"/>'
b+=text(260,543,'3 × 15 + 2 × 2 = 49 mm',25,'#168570',700,'middle')+text(260,576,'50 − 49 = 1 mm remaining',21,'#263346',400,'middle')
b+=text(28,638,'Arithmetic is only a first check.',23,weight=700)+text(28,669,'Test closure and movement on a sample.',19,'#657184')
svg('bead-pen-stack-length-example.svg',730,'Illustrative bead stack length calculation','Three 15 mm bead heights and two 2 mm spacers occupy 49 mm. A hypothetical 50 mm usable pen length leaves 1 mm. These are example dimensions, not a recommended clearance or a Qula Craft pen specification.',b)

title='How to Choose Pen Beads: Diameter, Hole Size & Fit Guide'
desc='Measure bead diameter, hole size and usable pen-rod length. Use illustrated sizing steps, a stack calculation and a wholesale checklist to choose pen beads.'
h1='How to Choose Beads for Pens: A Size & Fit Guide'
shell=(ROOT/'guide-beadable-pen-beads.html').read_text(encoding='utf-8')
pre=shell[:re.search(r'<main[^>]*>',shell).end()]
post=shell[shell.index('</main>'):]
url=BASE+SLUG
pre=pre.replace('https://www.qulacrafts.com/guide-beadable-pen-beads.html',url)
pre=re.sub(r'<title>.*?</title>',f'<title>{html.escape(title)}</title>',pre,flags=re.S)
for attr,key,value in [('name','description',desc),('property','og:title',title),('property','og:description',desc)]:
    pre=re.sub(rf'(<meta {attr}="{key}" content=")[^"]*(")',lambda m:m[1]+html.escape(value,quote=True)+m[2],pre)
def keep_schema(m):
    obj=json.loads(m[1])
    return m[0] if obj.get('@type') in ['Organization','WebSite'] else ''
pre=re.sub(r'<script type="application/ld\+json">(.*?)</script>',keep_schema,pre,flags=re.S)
hero=BASE+'assets/images/real-life-scenes-v1/real-life-beadable-pen-gift.webp'
schema=[{'@context':'https://schema.org','@type':'BlogPosting','headline':h1,'description':desc,'image':hero,'datePublished':'2026-10-01','dateModified':'2026-10-01','author':{'@id':BASE+'#organization'},'publisher':{'@id':BASE+'#organization'},'mainEntityOfPage':url}, {'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE},{'@type':'ListItem','position':2,'name':'Resources','item':BASE+'resources.html'},{'@type':'ListItem','position':3,'name':'Pen Bead Size & Fit Guide','item':url}]}]
content=(ROOT/'scripts/data/pen-bead-size-guide-body.html').read_text(encoding='utf-8')
faq=[]
for q,a in re.findall(r'<details><summary>(.*?)</summary><p>(.*?)</p></details>',content):
    faq.append({'@type':'Question','name':html.unescape(q),'acceptedAnswer':{'@type':'Answer','text':html.unescape(a)}})
schema.append({'@context':'https://schema.org','@type':'FAQPage','mainEntity':faq})
pre=pre.replace('</head>','<link rel="stylesheet" href="assets/css/pen-bead-guide.css?v=20261001">\n'+''.join('<script type="application/ld+json">'+json.dumps(s,ensure_ascii=False)+'</script>\n' for s in schema)+'</head>')
body=f'''<article class="pen-fit-article"><section class="page-hero"><div class="container narrow"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Home</a> / <a href="resources.html">Resources</a> / <span>Pen Bead Size &amp; Fit Guide</span></nav><span class="eyebrow">The Qula Craft Blog · Buying &amp; Making</span><h1>{html.escape(h1)}</h1><p>Bead diameter. Hole diameter. Usable rod length.<br>Measure the three things that decide whether your design works.</p><p class="small-note">October 1, 2026 · Qula Craft Sourcing Team</p></div></section><section class="section" style="padding-top:26px"><div class="container guide-body">{content}</div></section></article>'''
(ROOT/SLUG).write_text(pre+body+post,encoding='utf-8')
print('Built',SLUG,'and 3 original SVG diagrams.')
