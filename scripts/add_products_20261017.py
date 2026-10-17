"""Import the 10.16 supplemental supplied-photo batch, preserving source values and existing SKUs."""
import argparse, copy, hashlib, html, json, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from PIL import Image
from add_products_20261012 import card, save_json, sha256
from add_products_20261012_v3 import specs_from_source
from catalog_schema import catalog_list_item

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.qulacrafts.com/'
DATE = '2026-10-17'
PAGES = {'polymer-clay-slices':'polymer-clay-sprinkles.html','plastic-beads':'acrylic-beads.html'}
QUOTE = {'resin-charms':'Resin Charms','polymer-clay-slices':'Polymer Clay Sprinkles','plastic-beads':'Acrylic Beads','keychain':'Keychains','pvc-plastic-charms':'Other','beads-for-pens':'Beads for Pens','slime-charms':'Slime Charms'}
MIXED = 'RW20423/RW22336/RW22338'

def source_records(path):
    cells = json.loads(path.read_text())
    headers = list(cells[0].values())
    return {int(re.search(r'\d+',next(iter(row)))[0]):dict(zip(headers,row.values())) for row in cells[1:]}

def public_source_specs(raw, sku):
    adapted = dict(raw)
    sleeve = raw['包装规格'].strip() == '12pcs/sleeve'
    if sleeve: adapted['包装规格'] = '12pcs/bag'
    if sku == 'SLM-RX488':
        adapted['包装规格'] = '100pcs/bag'
        adapted['尺寸'] = '咨询客服'
        adapted['材质'] = 'Clay and other decorative components; confirm composition by selected mix'
    specs = specs_from_source(adapted)
    if sku == 'RW26826':
        specs['Size'] = 'Approximately 15 × 17 mm'
    if sku == 'RW25208':
        specs['Size'] = 'Approximately 20 × 40 mm'
    if sku == 'SLM-RX488':
        specs['Net weight per bag'] = 'Approximately 3 g'
        specs['Standard pack'] = '100 bags per outer pack; custom packing by inquiry'
    if sku == 'CDK003883/CDK003939/CDK003950/CDK00098':
        specs.pop('Size', None)
        specs['Pouch dimensions'] = 'Confirm by inquiry; source dimensions require verification'
        specs['Total length'] = '132 mm (source reference)'
    if raw['分类'].strip() == 'Jewelry keychain':
        specs['Hole'] = 'No separate stringing hole specified; supplied with keychain hardware'
    if sku == 'RW22581':
        specs['Hole'] = 'No stringing hole specified; nostril details are decorative'
    if '/' in sku or sku == 'RW3895-RW3857':
        specs['SKU group'] = 'Grouped assortment; confirm selected designs, individual sizes and mixture proportions by inquiry'
    if sleeve: specs['Standard pack'] = '12 pieces per sleeve'
    if raw['孔径'] == '有':
        specs['Hole'] = 'Stringing hole present; diameter not supplied. Confirm fit with a sample.'
        specs['Compatibility'] = 'Confirm the measured hole diameter against the intended cord or pen rod before ordering.'
    if sku == 'YQ029':
        specs['Hole'] = 'Flatback design shown; stringing hole not verified. Confirm attachment method with a sample.'
        specs['Material'] = 'Composition requires confirmation; source category lists acrylic, plastic and lucite'
        specs['Size range'] = '1.5–12 mm in the source title; confirm the selected size mix'
        specs.pop('Compatibility',None)
    if sku == 'YA012':
        specs['Size range'] = '4, 6, 8, 10, 12, 14, 16, 18 and 20 mm in source title; confirm selected sizes'
    if sku == 'CDK5013':
        specs['Material'] = 'Confirm clasp composition with the sample; source material field is a generic resin, clay and alloy listing'
        specs['Hole'] = 'Spring clasp opening; confirm mechanism and attachment dimensions with a sample'
    if sku.startswith('CDK') and sku != 'CDK5013':
        specs['Size'] = 'Heart component 50 mm; total length approximately 90 mm (source reference). Confirm each selected design.'
    if sku == 'RW26820':
        specs['Glow effect'] = 'Supplier-described luminous finish; confirm effect and performance with a sample'
    if sku == 'RW26821':
        specs['Hole'] = 'No separate stringing hole specified; the board-shaped handle includes a decorative opening. Confirm mounting method.'
    if sku == 'RW26825':
        specs['Attachment'] = 'Source says no hole. Confirm the fitting, loop or flatback configuration for each selected design.'
    if sku == 'RW337/285':
        specs.pop('Size',None)
        specs['RW337 dimensions'] = '32 × 32 × 12 mm'
        specs['RW285 dimensions'] = '15 × 17 × 11 mm'
        specs['SKU group'] = 'RW337 and RW285 in one grouped assortment; confirm selection and mixture proportions'
    if sku in {'RW26819','RW26828'}:
        specs['Size note'] = 'Source reference only; confirm individual design dimensions before ordering'
    specs['Packing and MOQ'] = 'Packing quantity is not the minimum order quantity. Confirm MOQ and dispatch date by inquiry.'
    return specs

original_public_source_specs = public_source_specs
def public_source_specs(raw, sku):
    specs=original_public_source_specs(raw,sku)
    plan=next(p for p in CURRENT_PLANS if p['sku']==sku)
    specs['Size']=plan['dimensions']
    specs['Selection note']=plan['factNote']
    if sku=='ABC041-ABC042':
        specs['Hole']='Source says no hole; the bead photo suggests a stringing design. Confirm hole presence and diameter by sample.'
    return specs

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--plan',type=Path,required=True)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--baseline',required=True)
    args=ap.parse_args()
    global CURRENT_PLANS
    plans=json.loads(args.plan.read_text()); CURRENT_PLANS=plans; records=source_records(args.source)
    assert len(plans)==15 and sum(p['operation']=='new' for p in plans)==14
    catpath=ROOT/'assets/data/product-catalog.json'; pdppath=ROOT/'assets/data/pdp-data.json'
    cat=json.loads(catpath.read_text()); pdp=json.loads(pdppath.read_text())
    copies=json.loads((ROOT/'assets/data/pdp-copy.json').read_text())
    details=json.loads((ROOT/'assets/data/pdp-description-details.json').read_text())
    oldcat=copy.deepcopy(cat); oldpdp=copy.deepcopy(pdp)
    previousSchemas={}
    for plan in plans:
        if plan['operation']=='update':
            previousSchemas[plan['sku']]=[m[0] for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',(ROOT/f'p-{plan["key"]}.html').read_text(),re.S) if json.loads(m[1]).get('@type') in {'Organization','WebSite'}]
    oldflat=[p for c in cat['categories'] for p in c['products']]
    assert len(oldflat)==336
    byslug={c['slug']:c for c in cat['categories']}; bysku={p['sku']:p for p in oldflat}
    pdpbykey={p['assetKey']:p for p in pdp}; additions={}; changed=[]; manifest=[]; batch={p['sku'] for p in plans}
    for plan in plans:
        sku,key=plan['sku'],plan['key']; raw=records[plan['sourceRow']]
        assert str(raw['sku']).strip()==sku
        images=plan['imagesLocal']; assert len(images)==len(set(images))==3
        imageinfo=[]
        for n,rel in enumerate(images,1):
            with Image.open(ROOT/rel) as im:
                w,h=im.size; assert 0<w<=1000 and not im.getexif()
            imageinfo.append({'path':rel,'role':['main','scene','detail'][n-1],'width':w,'height':h,'sha256':sha256(ROOT/rel),'bytes':(ROOT/rel).stat().st_size,'origin':plan['imageOrigins'][n-1]})
        w,h=imageinfo[0]['width'],imageinfo[0]['height']
        category=byslug[plan['category']]
        if plan['operation']=='new':
            assert sku not in bysku
            row={'category':category['name'],'categorySlug':category['slug'],'sourceSheet':'Sheet1','sourceRow':plan['sourceRow'],'sortOrder':0,'sku':sku,'title':plan['title'],'titleFull':plan['title'],'titleShort':plan['title'],'sourceTitle':raw['标题'],'sourceCategory':raw['分类'],'alibabaUrl':'','cleanAlibabaUrl':'','alibabaProductId':'','status':'ok','anchorNote':'','pdp':f'p-{key}.html'}
            entry={'catalogIndex':0,'assetKey':key,'sku':sku,'category':category['name'],'categorySlug':category['slug'],'url':'','status':'ok','reason':'','titleFull':raw['标题'],'moq':'','priceTiers':[],'stockStatus':'In stock; confirm the available quantity with your quote','specs':public_source_specs(raw,sku),'images':[],'sourceWorkbook':'10.11(9).xlsx','sourceSheet':'Sheet1','sourceRow':plan['sourceRow'],'sourceFields':raw,'importedAt':datetime.now(timezone.utc).isoformat(),'metaTitle':plan['metaTitle'],'metaDescription':plan['description'],'shortProductDescription':plan['description']}
            copies[key]={'sku':sku,'displayTitle':plan['title'],'metaTitle':plan['metaTitle'],'metaDescription':plan['description'],'isFamilyFriendly':True}; details[key]=plan['description']+' '+plan['uses']+' Confirm the selected designs, assortment, sample and destination when requesting a wholesale quote.'
            additions.setdefault(category['slug'],[]).append(row); pdp.append(entry)
        else:
            row=bysku[sku]; entry=pdpbykey[key]
            entry.update(specs={**entry.get('specs',{}), **public_source_specs(raw,sku)},sourceWorkbook='10.11(9).xlsx',sourceRow=plan['sourceRow'],sourceSheet='Sheet1',sourceFields=raw,stockStatus='In stock; confirm current available quantity by inquiry')
            if sku=='YA012': entry.update(priceTiers=[],moq='')
        row.update(image=images[0],imageAlt=sku+' '+row['title'],imageWidth=w,imageHeight=h,imageHash=hashlib.md5((ROOT/images[0]).read_bytes()).hexdigest())
        row['inquiryUrl']=f'quote.html?product={quote(sku+" "+row["title"],safe="")}&sku={quote(sku,safe="")}&image={quote(images[0],safe="/")}&category={quote(QUOTE[category["slug"]],safe="")}'
        entry['imagesLocal']=images; changed.append((plan,row,entry))
        manifest.append({'sku':sku,'operation':plan['operation'],'sourceRow':plan['sourceRow'],'sourceFields':raw,'sourceReferences':plan.get('sourceReferences',[{'file':plan['source'],'sha256':plan['sourceImageSha256']}]),'pdp':row['pdp'],'imageOutputs':imageinfo})
    for c in cat['categories']:
        c['products']=additions.get(c['slug'],[])+c['products']; c['productCount']=len(c['products'])
        for i,p in enumerate(c['products'],1):p['sortOrder']=i
    flat=[p for c in cat['categories'] for p in c['products']]; index={p['pdp']:i for i,p in enumerate(flat,1)}
    for e in pdp:e['catalogIndex']=index[f'p-{e["assetKey"]}.html']
    cat.update(totalProducts=len(flat),totalImages=len(flat),generatedAt=datetime.now(timezone.utc).isoformat())
    assert len(flat)==350
    for p,v,indent in [(catpath,cat,1),(pdppath,pdp,2),(ROOT/'assets/data/pdp-copy.json',copies,2),(ROOT/'assets/data/pdp-description-details.json',details,2)]:save_json(p,v,indent)
    # Use dimensions from previously approved HTML for existing related images.
    dimensions={}
    for p in ROOT.glob('*.html'):
        for tag in re.findall(r'<img\b[^>]+>',p.read_text()):
            attrs=dict(re.findall(r'(src|width|height)="([^"]*)"',tag))
            if all(k in attrs for k in ['src','width','height']):dimensions[attrs['src']]=(int(attrs['width']),int(attrs['height']))
    generator=(ROOT/'scripts/gen_pdp.py').read_text().split('# ---- 2)')[0]
    generator=generator.replace('for e in pdp:\n    sku, key','for e in pdp:\n    if e["sku"] not in BATCH_SKUS: continue\n    sku, key')
    generator=generator.replace('def img_dim(rel):','def img_dim(rel):\n    if not (SITE / rel).exists() and rel in APPROVED_DIMS: return APPROVED_DIMS[rel]')
    exec(compile(generator,str(ROOT/'scripts/gen_pdp.py'),'exec'),{'__file__':str(ROOT/'scripts/gen_pdp.py'),'BATCH_SKUS':batch,'APPROVED_DIMS':dimensions})
    for plan,row,e in changed:
        pagepath=ROOT/row['pdp']; page=pagepath.read_text()
        page=page.replace('detail view 2','source specification summary').replace('detail view 3','packing and order brief') if plan['operation']=='new' else page
        if plan['operation']=='new':
            page=page.replace('Decorative craft material — non-edible. Batch test reports (EN 71, ASTM F963, CPC, REACH) available on request.','Confirm the selected assortment, minimum order quantity and dispatch date with your inquiry.')
            page,n=re.subn(r'<div class="answer-box" style="margin:14px 0">.*?</div>','<div class="answer-box" style="margin:14px 0"><b>Wholesale pricing by quotation</b> · Minimum order quantity confirmed by inquiry.</div>',page,count=1,flags=re.S);assert n==1
        note=plan['galleryNote']
        marker='</div>\n<div>\n  <div class="answer-box"';assert marker in page
        page=page.replace(marker,'<p class="pdp-image-note" style="font-size:.85rem;color:#667085">'+note+' Props are not included; confirm selected designs and assortment before ordering.</p>'+marker,1)
        page,n=re.subn(r'quote\.html\?product=[^"<>]+',html.escape(row['inquiryUrl'],quote=True),page,count=1);assert n==1
        if row['sku'] in {'CZB26813','CZB26818','CZB26846'}:
            marker='</div>\n</section>'
            # Public specs already state that a stringing hole is not a fit guarantee.
            assert 'diameter not supplied' in page
        def entity_refs(m):
            schema=json.loads(m[1])
            if schema.get('@type')=='Product':
                schema['manufacturer']={'@id':BASE+'#organization'}
                if schema.get('offers'): schema['offers']['seller']={'@id':BASE+'#organization'}
            return '<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False,separators=(',',':'))+'</script>'
        page=re.sub(r'<script type="application/ld\+json">(.*?)</script>',entity_refs,page,flags=re.S)
        page=page.replace('</head>',''.join(previousSchemas.get(row['sku'],[]))+'</head>')
        pagepath.write_text('\n'.join(line.rstrip() for line in page.splitlines())+'\n')
    for slug in {p['category'] for p in plans}:
        path=ROOT/PAGES.get(slug,slug+'.html');page=path.read_text()
        updates={row['sku']:row for plan,row,e in changed if plan['operation']=='update' and plan['category']==slug}
        def update_card(m):
            s=html.unescape(re.search(r'<span class="pill soft">([^<]+)',m[0])[1])
            return card(updates[s]) if s in updates else m[0]
        page=re.sub(r'<article class="product-card"[^>]*>.*?</article>',update_card,page,flags=re.S)
        first=re.search(r'<article class="product-card"',page);assert first
        page=page[:first.start()]+''.join(card(p) for p in additions.get(slug,[]))+page[first.start():]
        def schema(m):
            v=json.loads(m[1])
            if v.get('@type')=='ItemList':v.update(numberOfItems=len(byslug[slug]['products']),itemListElement=[catalog_list_item(p,i) for i,p in enumerate(byslug[slug]['products'],1)])
            return '<script type="application/ld+json">'+json.dumps(v,ensure_ascii=False,separators=(',',':'))+'</script>'
        page=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,page,flags=re.S);path.write_text(page)
    xml=(ROOT/'sitemap.xml').read_text()
    for plan,row,e in changed:
        loc=BASE+row['pdp'];node='<url><loc>'+loc+'</loc><lastmod>'+DATE+'</lastmod><changefreq>monthly</changefreq><priority>0.7</priority>'+''.join(f'<image:image><image:loc>{BASE+p}</image:loc><image:title>{html.escape(row["sku"]+" "+row["title"])}</image:title></image:image>' for p in e['imagesLocal'])+'</url>'
        if plan['operation']=='new':assert loc not in xml;xml=xml.replace('</urlset>','  '+node+'\n</urlset>')
        else:xml,n=re.subn(r'<url>\s*<loc>'+re.escape(loc)+r'</loc>.*?</url>',lambda m:node,xml,flags=re.S);assert n==1
    (ROOT/'sitemap.xml').write_text(xml)
    for filename in ['llms-full.txt','llms.txt']:
        path=ROOT/filename;text=path.read_text().replace('336 live stock items','350 live stock items')
        if filename=='llms-full.txt':
            for slug,rows in additions.items():
                heading='## '+byslug[slug]['name']+'\n';assert heading in text
                text=text.replace(heading,heading+''.join(f'- [{p["title"]}]({BASE+p["pdp"]}): SKU {p["sku"]} · packing, MOQ and pricing by inquiry\n' for p in rows),1)
        path.write_text(text)
    protected={'sortOrder','image','imageAlt','imageWidth','imageHeight','imageHash','inquiryUrl'}
    now={p['pdp']:p for p in flat}
    for p in oldflat:
        ignored=protected if p['sku'] in batch else {'sortOrder'}
        assert {k:v for k,v in p.items() if k not in ignored}=={k:v for k,v in now[p['pdp']].items() if k not in ignored},p['sku']
    for old in oldpdp:
        cur=next(e for e in pdp if e['assetKey']==old['assetKey']);ignored={'catalogIndex','imagesLocal','specs','sourceWorkbook','sourceRow','sourceSheet','sourceFields','stockStatus','priceTiers','moq'} if old['sku'] in batch else {'catalogIndex'}
        assert {k:v for k,v in old.items() if k not in ignored}=={k:v for k,v in cur.items() if k not in ignored},old['sku']
    save_json(ROOT/'docs/product-batch-manifest-20261017.json',{'batchId':'qula-products-20261017','baselineCommit':args.baseline,'newProductCount':14,'updatedProductCount':1,'catalogCountBefore':336,'catalogCountAfter':350,'imageCount':45,'sourceWorkbook':'10.11(9).xlsx','products':manifest})
    print(json.dumps({'new':14,'updated':1,'catalog':350,'images':45}))

if __name__=='__main__':main()
