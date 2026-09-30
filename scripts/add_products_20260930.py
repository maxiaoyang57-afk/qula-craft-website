"""Add the confirmed QULA acrylic bead batch, keeping existing pages intact.

Run once from a clean latest-main checkout after copying the verified 21 images
into assets/images/pdp/<sku>/. Source: 9.30.xlsx and user correction 2026-09-30.
"""
import json, re, hashlib, html
from pathlib import Path
from urllib.parse import quote
from PIL import Image
from catalog_schema import catalog_list_item

ROOT=Path(__file__).resolve().parents[1]
BASE='https://www.qulacrafts.com/'
SKUS=['YA893','YA690','YJ145','YA449','YA425','YA417','YA382']
TITLES=['15mm AB Swirl Round Acrylic Beads','12 × 23mm AB Leaf Acrylic Beads','19mm AB Heart Acrylic Beads','16mm Textured Candy Acrylic Beads','16 × 18mm AB Heart Acrylic Beads with 2.5mm Hole','19 × 26mm Pig Acrylic Beads in White and Pink','Cupcake Acrylic Beads with Hole']
SIZES=['15 mm diameter','12 × 23 mm','19 mm','16 mm','16 × 18 mm','19 × 26 mm',None]
DESCS=[
 'Source 15mm AB swirl round acrylic beads in 100-piece bags. Ask Qula Craft about colors, hole diameter, customization and wholesale pricing.',
 'Source 12 × 23mm AB leaf acrylic beads in 100-piece bags for craft projects. Confirm hole fit, colors and wholesale pricing with Qula Craft.',
 'Shop 19mm AB heart acrylic beads in 100-piece bags for jewelry and craft projects. Ask Qula Craft about hole diameter, colors and bulk pricing.',
 'Source 16mm textured candy acrylic beads in 200-piece bags. Confirm hole diameter and pen compatibility, then request a wholesale quote.',
 'Source 16 × 18mm AB heart acrylic beads with a 2.5mm hole, packed in 500g bags. Ask Qula Craft about colors, customization and bulk pricing.',
 'Source 19 × 26mm pink and white pig acrylic beads in 100-piece bags. Ask Qula Craft about hole size, customization and wholesale pricing.',
 'Source cupcake-shaped acrylic beads in 100-piece bags for decorative craft projects. Confirm dimensions and hole size with Qula Craft before ordering.'
]
META=['15mm AB Swirl Acrylic Beads Wholesale | YA893','AB Leaf Acrylic Beads 12 × 23mm Wholesale | YA690','19mm AB Heart Acrylic Beads Wholesale | YJ145','16mm Textured Candy Acrylic Beads Wholesale | YA449','AB Heart Acrylic Beads with 2.5mm Hole | YA425','Pig Acrylic Beads 19 × 26mm Wholesale | YA417','Cupcake Acrylic Beads Wholesale | YA382']
SHAPES=['Round with swirl print','Leaf','Heart','Round with textured candy finish','Heart','Pig','Cupcake']
catpath=ROOT/'assets/data/product-catalog.json'; pdppath=ROOT/'assets/data/pdp-data.json'; copypath=ROOT/'assets/data/pdp-copy.json'
cat=json.loads(catpath.read_text());pdp=json.loads(pdppath.read_text());copies=json.loads(copypath.read_text())
flat=[p for c in cat['categories'] for p in c['products']]
assert not ({x['sku'].upper() for x in flat+pdp}&set(SKUS)), 'Existing SKU: stop to avoid overwrite'
category=next(c for c in cat['categories'] if c['slug']=='plastic-beads')
before=len(flat);old_cat_count=len(category['products']);new=[];entries=[];manifest=[]
for i,sku in enumerate(SKUS):
 key=sku.lower(); paths=sorted(str(p.relative_to(ROOT)) for p in (ROOT/f'assets/images/pdp/{key}').glob('*'))
 assert len(paths)==3 and all(f'{key}-{n}-' in paths[n-1] for n in (1,2,3)), (sku,paths)
 title=TITLES[i]; w,h=Image.open(ROOT/paths[0]).size;pack='500 g per bag' if sku=='YA425' else '200 pieces per bag' if sku=='YA449' else '100 pieces per bag'
 inquiry='quote.html?'+f'product={quote(sku+" "+title)}&sku={sku}&image={quote(paths[0],safe="/")}'
 row={'category':category['name'],'categorySlug':'plastic-beads','sourceSheet':'Sheet1','sourceRow':i+1,'sortOrder':i+1,'sku':sku,'title':title,'titleFull':title,'titleShort':title,'alibabaUrl':'','cleanAlibabaUrl':'','alibabaProductId':'','image':paths[0],'imageAlt':sku+' '+title,'imageWidth':w,'imageHeight':h,'imageHash':hashlib.md5((ROOT/paths[0]).read_bytes()).hexdigest(),'status':'ok','anchorNote':'','pdp':f'p-{key}.html','inquiryUrl':inquiry}
 specs={'Material':'Acrylic','Shape':SHAPES[i],'Pack reference':pack}
 if SIZES[i]:specs['Size']=SIZES[i]
 if sku=='YA425':specs['Hole diameter']='2.5 mm'
 specs['Customization']='Available; project details confirmed by quotation'
 specs['Order details']='Confirm minimum order quantity, sample timing and dispatch date by email'
 entry={'catalogIndex':0,'assetKey':key,'sku':sku,'category':category['name'],'categorySlug':'plastic-beads','url':'','status':'ok','reason':'','titleFull':title,'moq':'To be discussed','priceTiers':[],'stockStatus':'In stock; please confirm quantity and dispatch date','specs':specs,'images':[],'imagesLocal':paths,'fetchedAt':'2026-09-30T13:58:00Z','sourceWorkbook':'9.30.xlsx','sourceSheet':'Sheet1','sourceRow':i+1,'metaTitle':META[i],'metaDescription':DESCS[i],'shortProductDescription':DESCS[i],'publishingCheck':'Source main photo plus two AI-assisted presentation images; confirm dimensions and hole fit by quotation.'}
 copies[key]={'sku':sku,'displayTitle':title,'metaTitle':META[i],'metaDescription':DESCS[i],'isFamilyFriendly':True}
 assert 80<=len(DESCS[i])<=160
 new.append(row);entries.append(entry)
 manifest.append({'sku':sku,'sourceRow':i+1,'derivedTitle':title,'category':category['name'],'slug':row['pdp'],'duplicateStatus':'new','imageOutputs':[{'path':p,'role':r,'width':Image.open(ROOT/p).width,'height':Image.open(ROOT/p).height,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),'origin':'source photo' if n==0 else 'AI-assisted presentation'} for n,(p,r) in enumerate(zip(paths,['main','scene','detail']))],'listingStatus':'prepared','validationStatus':'pending','previewStatus':'pending'})
category['products']=new+category['products'];category['productCount']=len(category['products'])
for n,p in enumerate(category['products'],1):p['sortOrder']=n
flat=[p for c in cat['categories'] for p in c['products']];pdp.extend(entries)
indices={p['pdp']:i for i,p in enumerate(flat,1)}
for e in pdp:e['catalogIndex']=indices[f'p-{e["assetKey"]}.html']
cat.update(totalProducts=len(flat),totalImages=len(flat),generatedAt='2026-09-30T14:00:00Z')
for path,value,indent in [(catpath,cat,1),(pdppath,pdp,2),(copypath,copies,2)]:path.write_text(json.dumps(value,ensure_ascii=False,indent=indent)+'\n')

# Reuse the established PDP template, executing only its first stage for this
# new batch. Existing PDP files and unrelated shared sections are not regenerated.
source=(ROOT/'scripts/gen_pdp.py').read_text().split('# ---- 2)')[0]
source=source.replace('for e in pdp:\n    sku, key', 'for e in pdp:\n    if e["sku"] not in BATCH_SKUS: continue\n    sku, key')
exec(compile(source,str(ROOT/'scripts/gen_pdp.py'),'exec'),{'__file__':str(ROOT/'scripts/gen_pdp.py'),'BATCH_SKUS':set(SKUS)})
for row,e in zip(new,entries):
 p=ROOT/row['pdp'];s=p.read_text();key=e['assetKey'];sku=e['sku'];idx=SKUS.index(sku)
 s=s.replace('Decorative craft material — non-edible. Batch test reports (EN 71, ASTM F963, CPC, REACH) available on request.','Decorative craft components, not edible. Confirm specifications and intended use before ordering.')
 s=s.replace('</h1>', '</h1><p class="pdp-summary">'+html.escape(DESCS[idx])+'</p>',1)
 note='Hole diameter and pen or cord compatibility are confirmed before ordering.' if sku!='YA425' else 'The listed hole diameter is 2.5 mm. Check your pen rod or cord size before ordering.'
 if sku=='YA382':note='Please ask for the bead dimensions and hole diameter before ordering. '+note
 s=s.replace('<div class="pdp-cta"','<p>'+note+'</p><div class="pdp-cta"',1)
 s=s.replace('detail view 2','DIY styling illustration').replace('detail view 3','close-up styling illustration')
 marker='</div>\n<div>\n  <div class="answer-box"'
 assert marker in s
 s=s.replace(marker,'<p class="pdp-image-note" style="font-size:.85rem;color:#667085">Image 1: product photo. Images 2–3: styled illustrations. Props are not included.</p>'+marker,1)
 s=re.sub(r'quote\.html\?product=[^"<>]+',lambda m:html.escape(row['inquiryUrl'],quote=True),s,count=1)
 p.write_text(s)

def card(row):
 e=html.escape;sku=row['sku'];title=row['title'];wa=quote(f'Hello Qula Craft, I just viewed SKU {sku} and would like to discuss a custom quote. Can we chat?',safe='')
 return f'<article class="product-card" data-title="{e(title)}" data-type="Plastic Beads" data-use="plastic-beads"><div class="product-img"><a href="{row["pdp"]}" style="display:block"><img loading="lazy" src="{row["image"]}" alt="{e(row["imageAlt"])}" width="{row["imageWidth"]}" height="{row["imageHeight"]}"></a></div><div class="product-info"><span class="pill soft">{sku}</span><h3><a href="{row["pdp"]}" style="color:inherit;text-decoration:none">{e(title)}</a></h3><a class="btn btn-card" href="{e(row["inquiryUrl"],quote=True)}">Send Inquiry <span>→</span></a><div class="card-cta-row"><a class="wa-line" href="https://wa.me/8618632026595?text={wa}" target="_blank" rel="noopener">WhatsApp</a><a class="basket-add" data-sku="{sku}" data-title="{e(title)}">＋ Inquiry list</a></div></div></article>'
cp=ROOT/'acrylic-beads.html';s=cp.read_text();match=re.search(r'<article class="product-card"',s);assert match
s=s[:match.start()]+''.join(card(p) for p in new)+s[match.start():]
def replace_list(m):
 obj=json.loads(m[1])
 if obj.get('@type')=='ItemList':obj.update(numberOfItems=len(category['products']),itemListElement=[catalog_list_item(p,n) for n,p in enumerate(category['products'],1)])
 return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'</script>' if obj.get('@type')=='ItemList' else m[0]
s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',replace_list,s,flags=re.S);cp.write_text(s)
sp=ROOT/'sitemap.xml';s=sp.read_text()
for row,e in zip(new,entries):
 image_xml=''.join(f'<image:image><image:loc>{BASE+p}</image:loc><image:title>{html.escape(row["sku"]+" "+row["title"])}</image:title></image:image>' for p in e['imagesLocal'])
 s=s.replace('</urlset>',f'  <url><loc>{BASE+row["pdp"]}</loc><lastmod>2026-09-30</lastmod><changefreq>monthly</changefreq><priority>0.7</priority>{image_xml}</url>\n</urlset>')
s=re.sub(r'(<loc>https://www.qulacrafts.com/acrylic-beads.html</loc><lastmod>)[^<]+',r'\g<1>2026-09-30',s);sp.write_text(s)
lp=ROOT/'llms-full.txt';s=lp.read_text().replace(f'({before} live stock items)',f'({len(flat)} live stock items)')
marker='## Plastic Beads\n';assert marker in s;s=s.replace(marker,marker+''.join(f'- [{r["title"]}]({BASE+r["pdp"]}): SKU {r["sku"]} · {e["specs"]["Pack reference"]} · MOQ and pricing by quotation\n' for r,e in zip(new,entries)),1);lp.write_text(s)
(ROOT/'docs/product-batch-manifest-20260930.json').write_text(json.dumps({'batchId':'qula-acrylic-beads-20260930','target':'QULA','baselineCommit':'8a976288916c1739f6cbbbef4c2bd7fe52c804e0','mode':'preview','excludedSku':'YA680','correction':'YA382 is cupcake-shaped, confirmed by user','catalogCountBefore':before,'catalogCountAfter':len(flat),'categoryCountBefore':old_cat_count,'categoryCountAfter':len(category['products']),'priorityOrder':SKUS,'products':manifest},ensure_ascii=False,indent=2)+'\n')
print(f'Added {len(new)} products, 21 images; category {old_cat_count} → {len(category["products"])}; catalog {before} → {len(flat)}')
